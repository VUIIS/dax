/*
 * web: org.nrg.xnat.archive.GradualDicomImporter
 * XNAT http://www.xnat.org
 * Copyright (c) 2005-2017, Washington University School of Medicine and Howard Hughes Medical Institute
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.nrg.xnat.archive;

import com.google.common.base.Objects;
import com.google.common.base.Strings;
import com.google.common.io.ByteStreams;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.time.DateUtils;
import org.dcm4che2.data.*;
import org.dcm4che2.io.DicomInputStream;
import org.dcm4che2.io.DicomOutputStream;
import org.dcm4che2.io.StopTagInputHandler;
import org.dcm4che2.util.TagUtils;
import org.nrg.action.ClientException;
import org.nrg.action.ServerException;
import org.nrg.config.entities.Configuration;
import org.nrg.dcm.Decompress;
import org.nrg.dicom.mizer.service.*;
import org.nrg.dicomtools.filters.DicomFilterService;
import org.nrg.dicomtools.filters.SeriesImportFilter;
import org.nrg.framework.constants.PrearchiveCode;
import org.nrg.xdat.XDAT;
import org.nrg.xdat.om.ArcProject;
import org.nrg.xdat.om.XnatProjectdata;
import org.nrg.xft.db.PoolDBUtils;
import org.nrg.xft.security.UserI;
import org.nrg.xnat.DicomObjectIdentifier;
import org.nrg.xnat.Files;
import org.nrg.xnat.Labels;
import org.nrg.xnat.helpers.merge.anonymize.DefaultAnonUtils;
import org.nrg.xnat.helpers.prearchive.DatabaseSession;
import org.nrg.xnat.helpers.prearchive.PrearcDatabase;
import org.nrg.xnat.helpers.prearchive.PrearcDatabase.Either;
import org.nrg.xnat.helpers.prearchive.PrearcUtils;
import org.nrg.xnat.helpers.prearchive.PrearcUtils.SessionFileLockException;
import org.nrg.xnat.helpers.prearchive.SessionData;
import org.nrg.xnat.helpers.uri.URIManager;
import org.nrg.xnat.restlet.actions.importer.ImporterHandler;
import org.nrg.xnat.restlet.actions.importer.ImporterHandlerA;
import org.nrg.xnat.restlet.util.FileWriterWrapperI;
import org.nrg.xnat.services.cache.UserProjectCache;
import org.nrg.xnat.turbine.utils.ArcSpecManager;
import org.restlet.data.Status;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.MalformedURLException;
import java.util.*;
import java.util.concurrent.Callable;

@SuppressWarnings("ThrowFromFinallyBlock")
@Service
@ImporterHandler(handler = ImporterHandlerA.GRADUAL_DICOM_IMPORTER)
public class GradualDicomImporter extends ImporterHandlerA {
    public static final String SENDER_AE_TITLE_PARAM = "Sender-AE-Title";
    public static final String SENDER_ID_PARAM       = "Sender-ID";
    public static final String TSUID_PARAM           = "Transfer-Syntax-UID";

    public GradualDicomImporter(final Object listenerControl,
                                final UserI user,
                                final FileWriterWrapperI fileWriter,
                                final Map<String, Object> parameters)
            throws IOException, ClientException {
        super(listenerControl, user, fileWriter, parameters);
        _user = user;
        _userId = user.getUsername();
        _fileWriter = fileWriter;
        _parameters = parameters;
        if (_parameters.containsKey(TSUID_PARAM)) {
            _transferSyntax = TransferSyntax.valueOf((String) _parameters.get(TSUID_PARAM));
        }
        _cache = XDAT.getContextService().getBean(UserProjectCache.class);
    }

    @Override
    public List<String> call() throws ClientException, ServerException {
        final String name = _fileWriter.getName();
        final DicomObject dicom;
        final XnatProjectdata project;
        final DicomObjectIdentifier<XnatProjectdata> dicomObjectIdentifier = getIdentifier();
        try (final BufferedInputStream bis = new BufferedInputStream(_fileWriter.getInputStream());
             final DicomInputStream dis = null == _transferSyntax ? new DicomInputStream(bis) : new DicomInputStream(bis, _transferSyntax)) {
            final int lastTag = Math.max(dicomObjectIdentifier.getTags().last(), Tag.SeriesDescription) + 1;
            logger.trace("reading object into memory up to {}", TagUtils.toString(lastTag));
            dis.setHandler(new StopTagInputHandler(lastTag));
            dicom = dis.readDicomObject();
            
            // begin VUIIS customization
            VuiisDicomObjectFilter.filter(dicom);
            // end VUIIS customization

            logger.trace("handling file with query parameters {}", _parameters);
            try {
                // project identifier is expensive, so avoid if possible
                project = getProject(PrearcUtils.identifyProject(_parameters),
                                     new Callable<XnatProjectdata>() {
                                         public XnatProjectdata call() {
                                             return dicomObjectIdentifier.getProject(dicom);
                                         }
                                     });
            } catch (MalformedURLException e1) {
                logger.error("unable to parse supplied destination flag", e1);
                throw new ClientException(Status.CLIENT_ERROR_BAD_REQUEST, e1);
            }
            final String projectId = project != null ? (String) project.getProps().get("id") : null;
            final SeriesImportFilter siteFilter = getDicomFilterService().getSeriesImportFilter();
            final SeriesImportFilter projectFilter = StringUtils.isNotBlank(projectId) ? getDicomFilterService().getSeriesImportFilter(projectId) : null;
            if (logger.isDebugEnabled()) {
                if (siteFilter != null) {
                    if (projectFilter != null) {
                        logger.debug("Found " + (siteFilter.isEnabled() ? "enabled" : "disabled") + " site-wide series import filter and " + (siteFilter.isEnabled() ? "enabled" : "disabled") + " series import filter for the project " + projectId);
                    } else if (StringUtils.isNotBlank(projectId)) {
                        logger.debug("Found " + (siteFilter.isEnabled() ? "enabled" : "disabled") + " site-wide series import filter and no series import filter for the project " + projectId);
                    } else {
                        logger.debug("Found a site-wide series import filter and no project ID was specified");
                    }
                } else if (projectFilter != null) {
                    logger.debug("Found no site-wide series import filter and " + (projectFilter.isEnabled() ? "enabled" : "disabled") + " series import filter for the project " + projectId);
                }
            }
            if (!(shouldIncludeDicomObject(siteFilter, dicom) && shouldIncludeDicomObject(projectFilter, dicom))) {
                return new ArrayList<>();
                /* TODO: Return information to user on rejected files. Unfortunately throwing an
                 * exception causes DicomBrowser to display a panicked error message. Some way of
                 * returning the information that a particular file type was not accepted would be
                 * nice, though. Possibly record the information and display on an admin page.
                 * Work to be done for 1.7
                 */
            }
            try {
                bis.reset();
            } catch (IOException e) {
                logger.error("unable to reset DICOM data stream", e);
            }
            if (Strings.isNullOrEmpty(dicom.getString(Tag.SOPClassUID))) {
                throw new ClientException("object " + name + " contains no SOP Class UID");
            }
            if (Strings.isNullOrEmpty(dicom.getString(Tag.SOPInstanceUID))) {
                throw new ClientException("object " + name + " contains no SOP Instance UID");
            }

            final String studyInstanceUID = dicom.getString(Tag.StudyInstanceUID);
            logger.trace("Looking for study {} in project {}", studyInstanceUID, null == project ? null : project.getId());

            // Fill a SessionData object in case it is the first upload
            final File root;
            if (null == project) {
                root = new File(ArcSpecManager.GetInstance().getGlobalPrearchivePath());
            } else {
                //root = new File(project.getPrearchivePath());
                root = new File(ArcSpecManager.GetInstance().getGlobalPrearchivePath() + "/" + project.getId());
            }

            final String sessionLabel;
            if (_parameters.containsKey(URIManager.EXPT_LABEL)) {
                sessionLabel = (String) _parameters.get(URIManager.EXPT_LABEL);
                logger.trace("using provided experiment label {}", _parameters.get(URIManager.EXPT_LABEL));
            } else {
                sessionLabel = StringUtils.defaultIfBlank(dicomObjectIdentifier.getSessionLabel(dicom), "dicom_upload");
            }

            final String visit;
            if (_parameters.containsKey(URIManager.VISIT_LABEL)) {
                visit = (String) _parameters.get(URIManager.VISIT_LABEL);
                logger.trace("using provided visit label {}", _parameters.get(URIManager.VISIT_LABEL));
            } else {
                visit = null;
            }

            final String subject;
            if (_parameters.containsKey(URIManager.SUBJECT_ID)) {
                subject = (String) _parameters.get(URIManager.SUBJECT_ID);
            } else {
                subject = dicomObjectIdentifier.getSubjectLabel(dicom);
            }

            final File timestamp = new File(root, PrearcUtils.makeTimestamp());

            if (null == subject) {
                logger.trace("subject is null for session {}/{}", timestamp, sessionLabel);
            }

            // Query the cache for an existing session that has this Study Instance UID, project name, and optional modality.
            // If found the SessionData object we just created is over-ridden with the values from the cache.
            // Additionally a record of which operation was performed is contained in the Either<SessionData,SessionData>
            // object returned.
            //
            // This record is necessary so that, if this row was created by this call, it can be deleted if anonymization
            // goes wrong. In case of any other error the file is left on the filesystem.
            final Either<SessionData, SessionData> getOrCreate;
            final SessionData session;
            try {
                final SessionData initialize = new SessionData();
                initialize.setFolderName(sessionLabel);
                initialize.setName(sessionLabel);
                initialize.setProject(project == null ? null : project.getId());
                initialize.setVisit(visit);
                initialize.setScan_date(dicom.getDate(Tag.StudyDate));
                initialize.setTag(studyInstanceUID);
                initialize.setTimestamp(timestamp.getName());
                initialize.setStatus(PrearcUtils.PrearcStatus.RECEIVING);
                initialize.setLastBuiltDate(Calendar.getInstance().getTime());
                initialize.setSubject(subject);
                initialize.setUrl((new File(timestamp, sessionLabel)).getAbsolutePath());
                initialize.setSource(_parameters.get(URIManager.SOURCE));
                initialize.setPreventAnon(Boolean.valueOf((String) _parameters.get(URIManager.PREVENT_ANON)));
                initialize.setPreventAutoCommit(Boolean.valueOf((String) _parameters.get(URIManager.PREVENT_AUTO_COMMIT)));

                getOrCreate = PrearcDatabase.eitherGetOrCreateSession(initialize, timestamp, shouldAutoArchive(project, dicom));

                if (getOrCreate.isLeft()) {
                    session = getOrCreate.getLeft();
                } else {
                    session = getOrCreate.getRight();
                }
            } catch (Exception e) {
                throw new ServerException(Status.SERVER_ERROR_INTERNAL, e);
            }

            try {
                // else if the last mod time is more then 15 seconds ago, update it.
                // this code builds and executes the sql directly, because the APIs for doing so generate multiple SELECT statements (to confirm the row is there)
                // we've confirmed the row is there in line 338, so that shouldn't be necessary here.
                // this code executes for every file received, so any unnecessary sql should be eliminated.
                if (Calendar.getInstance().getTime().after(DateUtils.addSeconds(session.getLastBuiltDate(), 15))) {
                    PoolDBUtils.ExecuteNonSelectQuery(DatabaseSession.updateSessionLastModSQL(session.getName(), session.getTimestamp(), session.getProject()), null, null);
                }
            } catch (Exception e) {
                logger.error("An error occurred trying to update the session update timestamp.", e);
            }

            // Build the scan label
            final String seriesNum = dicom.getString(Tag.SeriesNumber);
            final String seriesUID = dicom.getString(Tag.SeriesInstanceUID);
            final String scan;
            if (Files.isValidFilename(seriesNum)) {
                scan = seriesNum;
            } else if (!Strings.isNullOrEmpty(seriesUID)) {
                scan = Labels.toLabelChars(seriesUID);
            } else {
                scan = null;
            }

            final String source = getString(_parameters, SENDER_ID_PARAM, _user.getLogin());

            final DicomObject fmi;
            if (dicom.contains(Tag.TransferSyntaxUID)) {
                fmi = dicom.fileMetaInfo();
            } else {
                final String sopClassUID = dicom.getString(Tag.SOPClassUID);
                final String sopInstanceUID = dicom.getString(Tag.SOPInstanceUID);
                final String transferSyntaxUID;
                if (null == _transferSyntax) {
                    transferSyntaxUID = dicom.getString(Tag.TransferSyntaxUID, DEFAULT_TRANSFER_SYNTAX);
                } else {
                    transferSyntaxUID = _transferSyntax.uid();
                }
                fmi = new BasicDicomObject();
                fmi.initFileMetaInformation(sopClassUID, sopInstanceUID, transferSyntaxUID);
                if (_parameters.containsKey(SENDER_AE_TITLE_PARAM)) {
                    fmi.putString(Tag.SourceApplicationEntityTitle, VR.AE, (String) _parameters.get(SENDER_AE_TITLE_PARAM));
                }
            }

            final File sessionFolder = new File(new File(root, session.getTimestamp()), session.getFolderName());
            final File outputFile = getSafeFile(sessionFolder, scan, name, dicom, Boolean.valueOf((String) _parameters.get(RENAME_PARAM)));
            outputFile.getParentFile().mkdirs();

            final PrearcUtils.PrearcFileLock lock;
            try {
                lock = PrearcUtils.lockFile(session.getSessionDataTriple(), outputFile.getName());
                write(fmi, dicom, bis, outputFile, source);
            } catch (IOException e) {
                throw new ServerException(Status.SERVER_ERROR_INSUFFICIENT_STORAGE, e);
            } catch (SessionFileLockException e) {
                throw new ClientException("Concurrent file sends of the same data is not supported.");
            }
            try {
                // check to see of this session came in through an application that may have performed anonymization
                // prior to transfer, e.g. the XNAT Upload Assistant.
                if (!session.getPreventAnon() && DefaultAnonUtils.getService().isSiteWideScriptEnabled()) {
                    Configuration c = DefaultAnonUtils.getCachedSitewideAnon();
                    if (c != null && c.getStatus().equals(Configuration.ENABLED_STRING)) {
                        //noinspection deprecation

                        final MizerService service = XDAT.getContextService().getBeanSafely(MizerService.class);
                        service.anonymize(outputFile, session.getProject(), session.getSubject(), session.getFolderName(), true, c.getId(), c.getContents());

                    } else {
                        logger.debug("Anonymization is not enabled, allowing session {} {} {} to proceed without anonymization.", session.getProject(), session.getSubject(), session.getName());
                    }
                } else if (session.getPreventAnon()) {
                    logger.debug("The session {} {} {} has already been anonymized by the uploader, proceeding without further anonymization.", session.getProject(), session.getSubject(), session.getName());
                }
            } catch (Throwable e) {
                logger.debug("Dicom anonymization failed: " + outputFile, e);
                try {
                    // if we created a row in the database table for this session
                    // delete it.
                    if (getOrCreate.isRight()) {
                        PrearcDatabase.deleteSession(session.getFolderName(), session.getTimestamp(), session.getProject());
                    } else {
                        outputFile.delete();
                    }
                } catch (Throwable t) {
                    logger.debug("Unable to delete relevant file :" + outputFile, e);
                    throw new ServerException(Status.SERVER_ERROR_INTERNAL, t);
                }
                throw new ServerException(Status.SERVER_ERROR_INTERNAL, e);
            } finally {
                //release the file lock
                lock.release();
            }

            logger.trace("Stored object {}/{}/{} as {} for {}", project, studyInstanceUID, dicom.getString(Tag.SOPInstanceUID), session.getUrl(), source);
            return Collections.singletonList(session.getExternalUrl());
        } catch (ClientException e) {
            throw e;
        } catch (Throwable t) {
            throw new ClientException(Status.CLIENT_ERROR_BAD_REQUEST, "unable to read DICOM object " + name, t);
        }

    }

    private boolean canCreateIn(final XnatProjectdata p) {
        try {
            return PrearcUtils.canModify(_user, p.getId());
        } catch (Throwable t) {
            logger.error("Unable to check permissions for " + _user + " in " + p, t);
            return false;
        }
    }

    private XnatProjectdata getProject(final String alias, final Callable<XnatProjectdata> lookupProject) {
        if (null != alias) {
            logger.debug("looking for project matching alias {} from query parameters", alias);
            final XnatProjectdata project = _cache.get(_user, alias);
            if (project != null) {
                logger.info("Storage request specified project or alias {}, found accessible project {}", alias, project.getId());
                return project;
            }
            logger.info("storage request specified project {}, which does not exist or user does not have create perms", alias);
        } else {
            logger.trace("no project alias found in query parameters");
        }

        // No alias, or we couldn't match it to a project. Run the identifier to see if that can get a project name/alias.
        // (Don't cache alias->identifier-derived-project because we didn't use the alias to derive the project.)
        try {
            return null == lookupProject ? null : lookupProject.call();
        } catch (Throwable t) {
            logger.error("error in project lookup", t);
            return null;
        }
    }

    private File getSafeFile(File sessionDir, String scan, String name, DicomObject o, boolean forceRename) {
        String fileName = getNamer().makeFileName(o);
        while (fileName.charAt(0) == '.') {
            fileName = fileName.substring(1);
        }
        final File safeFile = Files.getImageFile(sessionDir, scan, fileName);
        if (forceRename) {
            return safeFile;
        }
        final String valname = Files.toFileNameChars(name);
        if (!Files.isValidFilename(valname)) {
            return safeFile;
        }
        final File reqFile = Files.getImageFile(sessionDir, scan, valname);
        if (reqFile.exists()) {
            try (final FileInputStream fin = new FileInputStream(reqFile)) {
                final DicomObject o1 = read(fin, name);
                if (Objects.equal(o.get(Tag.SOPInstanceUID), o1.get(Tag.SOPInstanceUID)) &&
                    Objects.equal(o.get(Tag.SOPClassUID), o1.get(Tag.SOPClassUID))) {
                    return reqFile;  // object are equivalent; ok to overwrite
                } else {
                    return safeFile;
                }
            } catch (Throwable t) {
                return safeFile;
            }
        } else {
            return reqFile;
        }
    }

    private boolean shouldIncludeDicomObject(final SeriesImportFilter filter, final DicomObject dicom) {
        // If we don't have a filter or the filter is turned off, then we include the DICOM object by default (no filtering)
        if (filter == null || !filter.isEnabled()) {
            return true;
        }
        final boolean shouldInclude = filter.shouldIncludeDicomObject(dicom);
        if (logger.isDebugEnabled()) {
            final String association = StringUtils.isBlank(filter.getProjectId()) ? "site" : "project " + filter.getProjectId();
            logger.debug("The series import filter for " + association + " indicated a DICOM object from series \"" + dicom.get(Tag.SeriesDescription).getString(dicom.getSpecificCharacterSet(), true) + "\" " + (shouldInclude ? "should" : "shouldn't") + " be included.");
        }
        return shouldInclude;
    }

    private DicomFilterService getDicomFilterService() {
        if (_filterService == null) {
            synchronized (logger) {
                _filterService = XDAT.getContextService().getBean(DicomFilterService.class);
            }
        }
        return _filterService;
    }

    private PrearchiveCode shouldAutoArchive(final XnatProjectdata project, final DicomObject o) {
        if (null == project) {
            return null;
        }
        Boolean fromDicomObject = getIdentifier().requestsAutoarchive(o);
        if (fromDicomObject != null) {
            return fromDicomObject ? PrearchiveCode.AutoArchive : PrearchiveCode.Manual;
        }
        ArcProject arcProject = project.getArcSpecification();
        if (arcProject == null) {
            logger.warn("Tried to get the arc project from project {}, but got null in return. Returning null for the prearchive code, but it's probably not good that the arc project wasn't found.", project.getId());
            return null;
        }
        return PrearchiveCode.code(arcProject.getPrearchiveCode());
    }

    private static boolean initializeCanDecompress() {
        try {
            return Decompress.isSupported();
        } catch (NoClassDefFoundError error) {
            return false;
        }
    }

    private static <K, V> String getString(final Map<K, V> m, final K k, final V defaultValue) {
        final V v = m.get(k);
        if (null == v) {
            return null == defaultValue ? null : defaultValue.toString();
        } else {
            return v.toString();
        }
    }

    private static DicomObject read(final InputStream in, final String name) throws ClientException {
        try (final BufferedInputStream bis = new BufferedInputStream(in);
             final DicomInputStream dis = new DicomInputStream(bis)) {
            final DicomObject o = dis.readDicomObject();
            if (Strings.isNullOrEmpty(o.getString(Tag.SOPClassUID))) {
                throw new ClientException("object " + name + " contains no SOP Class UID");
            }
            if (Strings.isNullOrEmpty(o.getString(Tag.SOPInstanceUID))) {
                throw new ClientException("object " + name + " contains no SOP Instance UID");
            }
            return o;
        } catch (IOException e) {
            throw new ClientException(Status.CLIENT_ERROR_BAD_REQUEST, "unable to parse or close DICOM object", e);
        }
    }

    private static void write(final DicomObject fmi, final DicomObject dataset, final BufferedInputStream remainder, final File f, final String source)
            throws ClientException, IOException {
        IOException ioexception = null;
        final FileOutputStream fos = new FileOutputStream(f);
        final BufferedOutputStream bos = new BufferedOutputStream(fos);
        try {
            final DicomOutputStream dos = new DicomOutputStream(bos);
            try {
                final String tsuid = fmi.getString(Tag.TransferSyntaxUID, DEFAULT_TRANSFER_SYNTAX);
                try {
                    if (Decompress.needsDecompress(tsuid) && canDecompress) {
                        try {
                            // Read the rest of the object into memory so the pixel data can be decompressed.
                            final DicomInputStream dis = new DicomInputStream(remainder, tsuid);
                            try {
                                dis.readDicomObject(dataset, -1);
                            } catch (IOException e) {
                                ioexception = e;
                                throw new ClientException(Status.CLIENT_ERROR_BAD_REQUEST,
                                                          "error parsing DICOM object", e);
                            }
                            final ByteArrayInputStream bis = new ByteArrayInputStream(Decompress.dicomObject2Bytes(dataset, tsuid));
                            final DicomObject d = Decompress.decompress_image(bis, tsuid);
                            final String dtsdui = Decompress.getTsuid(d);
                            try {
                                fmi.putString(Tag.TransferSyntaxUID, VR.UI, dtsdui);
                                dos.writeFileMetaInformation(fmi);
                                dos.writeDataset(d.dataset(), dtsdui);
                            } catch (Throwable t) {
                                if (t instanceof IOException) {
                                    ioexception = (IOException) t;
                                } else {
                                    logger.error("Unable to write decompressed dataset", t);
                                }
                                try {
                                    dos.close();
                                } catch (IOException e) {
                                    throw ioexception = null == ioexception ? e : ioexception;
                                }
                            }
                        } catch (ClientException e) {
                            throw e;
                        } catch (Throwable t) {
                            logger.error("Decompression failed; storing in original format " + tsuid, t);
                            dos.writeFileMetaInformation(fmi);
                            dos.writeDataset(dataset, tsuid);
                            if (null != remainder) {
                                final long copied = ByteStreams.copy(remainder, bos);
                                logger.trace("copied {} additional bytes to {}", copied, f);
                            }
                        }
                    } else {
                        dos.writeFileMetaInformation(fmi);
                        dos.writeDataset(dataset, tsuid);
                        if (null != remainder) {
                            final long copied = ByteStreams.copy(remainder, bos);
                            logger.trace("copied {} additional bytes to {}", copied, f);
                        }
                    }
                } catch (NoClassDefFoundError t) {
                    logger.error("Unable to check compression status; storing in original format " + tsuid, t);
                    dos.writeFileMetaInformation(fmi);
                    dos.writeDataset(dataset, tsuid);
                    if (null != remainder) {
                        final long copied = ByteStreams.copy(remainder, bos);
                        logger.trace("copied {} additional bytes to {}", copied, f);
                    }
                }
            } catch (IOException e) {
                throw ioexception = null == ioexception ? e : ioexception;
            } finally {
                try {
                    dos.close();
                    LoggerFactory.getLogger("org.nrg.xnat.received").info("{}:{}", source, f);
                } catch (IOException e) {
                    throw null == ioexception ? e : ioexception;
                }
            }
        } catch (IOException e) {
            throw ioexception = e;
        } finally {
            try {
                bos.close();
            } catch (IOException e) {
                throw null == ioexception ? e : ioexception;
            }
        }
    }

    private static final Logger  logger                  = LoggerFactory.getLogger(GradualDicomImporter.class);
    private static final String  DEFAULT_TRANSFER_SYNTAX = TransferSyntax.ImplicitVRLittleEndian.uid();
    private static final String  RENAME_PARAM            = "rename";
    private static final boolean canDecompress           = initializeCanDecompress();

    private final UserProjectCache    _cache;
    private final FileWriterWrapperI  _fileWriter;
    private final UserI               _user;
    private final String              _userId;
    private final Map<String, Object> _parameters;

    private TransferSyntax     _transferSyntax;
    private DicomFilterService _filterService;
}
