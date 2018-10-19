function [scan_detail_file,sess_detail_file] = XnatDetailedReport( ...
	scan_file,assr_file,out_dir)
% MATLAB R2015b+ function to merge XNAT scan and assessor reports for a
% project, to generate human-readable lists of assessor status indexed by
% scan and session. Example function call:
%    [scan_detail_file,sess_detail_file] = XnatDetailedReport( ...
%    	'report_scan.csv','report_assr.csv','.')
%
% Requires commit b81943a or later of DAX (https://github.com/VUIIS/dax) so
% that Xnatreport quotes fields correctly in its output.
%
% INPUTS
%
% scan_file   CSV output of Xnatreport run with the specific command line
%             Xnatreport -p <project> -c report_scan.csv --format \
%             object_type,project_id,subject_label,session_label,scan_id,type,series_description,quality,note
%
% assr_file   CSV output of Xnatreport run with the specific command line
%             Xnatreport -p <project> -c report_assr.csv --format \
%             object_type,project_id,subject_label,session_label,assessor_label,proctype,procstatus,qcstatus,version
%
% out_dir     Where the output files detailed_report_scan.csv and
%             detailed_report_sess.csv will be saved.
%
% Multiple projects may be specified on the Xnatreport command lines in the
% usual way using a comma separated list. See the adjacent file
% generate_xnat_reports.sh for a complete example.
%
%
% OUTPUTS
%
% Two detailed reports are produced:
%
% detailed_report_scan.csv   For scan assessors. Each scan gets a row, and
%                            columns are added for the status of each
%                            associated scan assessor.
%
% detailed_report_sess.csv   For session assessors. Each session gets a row,
%                            and columns are added for the status of each
%                            associated session assessor.
%
%
% It shouldn't be too hard to refactor this in python using pandas data
% frames if that is needed. Essentially we're just joining tables.

% Read data from Xnatreport output. We rely on very specific formats here.
disp('Reading Xnatreports')
scan = readtable(scan_file, ...
	'Format','%C%C%C%C%C%q%q%q%q', ...
	'HeaderLines',2);
assr = readtable(assr_file, ...
	'Format','%C%C%C%C%C%q%q%q%q', ...
	'HeaderLines',2);

% These fields should not be empty. If they are, we replace the contents
% with "MISSING" so they'll be easy to notice.
assr.proctype(cellfun(@isempty,assr.proctype)) = {'MISSING'};
assr.procstatus(cellfun(@isempty,assr.procstatus)) = {'MISSING'};
assr.qcstatus(cellfun(@isempty,assr.qcstatus)) = {'MISSING'};


% We need the scan IDs in the assessor table - extract them from assessor
% labels and put them in a new column. While we're at it, label the session
% assessors as such based on their lack of a scan ID in the assessor label.
%
% There is probably some much faster way to do this with cellfun or varfun
% but that code comes out almost unreadable so we'll just be patient.
disp('Extracting assessor scan_id')
warning('off','MATLAB:table:RowsAddedNewVars')
for h = 1:height(assr)
	q = strsplit(char(assr.assessor_label(h)),'-x-');
	if length(q)==5
		assr.scan_id{h} = q{4};
	else
		assr.scan_id{h} = 'sess';
	end
end
assr.scan_id = categorical(assr.scan_id);

% Identify all proctypes that are present for scan and session assessors.
proctypes_scan = cellstr(unique(assr.proctype(assr.scan_id~='sess')));
proctypes_sess = cellstr(unique(assr.proctype(assr.scan_id=='sess')));


% One scan assessor type at a time, make a table whose columns contain the
% assessor status info for each scan, and merge it with the existing scan
% table.
disp('Merging for scans')
newscan = scan;
newscan.object_type = [];
for p = 1:length(proctypes_scan)
	thisassr = assr(strcmp(assr.proctype,proctypes_scan{p}),:);
	thisassr = thisassr(:, ...
		{'project_id','subject_label','session_label','scan_id', ...
		'procstatus','qcstatus','version'});
	thisassr.Properties.VariableNames{'procstatus'} = ...
		[proctypes_scan{p} '_procstatus'];
	thisassr.Properties.VariableNames{'qcstatus'} = ...
		[proctypes_scan{p} '_qcstatus'];
	thisassr.Properties.VariableNames{'version'} = ...
		[proctypes_scan{p} '_version'];
	
	newscan = outerjoin( ...
		newscan, ...
		thisassr, ...
		'Keys',{'project_id','subject_label','session_label','scan_id'}, ...
		'MergeKeys', true, ...
		'Type','Left' ...
		);
	
end

% Save the scan assessor table to file. We will timestamp it according to
% the modification time of the XNAT assessor report.
disp('Writing scan data to file')
d = dir(assr_file);
timestamp = datestr(d.date,'yyyymmddHHMMSS');
scan_detail_file = fullfile(out_dir, ...
	['detailed_report_scan_' timestamp '.csv']);
writetable(newscan,scan_detail_file,'QuoteStrings',true)


% Now for session assessors. One session assessor type at a time, make a
% table whose columns contain the assessor status info for each session,
% and merge it with the existing session table.
if isempty(proctypes_sess)
	
	disp('No session assessors found')

else
	
	disp('Merging for sessions')
	for p = 1:length(proctypes_sess)
		thisassr = assr(strcmp(assr.proctype,proctypes_sess{p}),:);
		thisassr = thisassr(:, ...
			{'project_id','subject_label','session_label', ...
			'procstatus','qcstatus','version'});
		thisassr.Properties.VariableNames{'procstatus'} = ...
			[proctypes_sess{p} '_procstatus'];
		thisassr.Properties.VariableNames{'qcstatus'} = ...
			[proctypes_sess{p} '_qcstatus'];
		thisassr.Properties.VariableNames{'version'} = ...
			[proctypes_sess{p} '_version'];
		
		if p==1
			newsess = thisassr;
		else
			newsess = outerjoin( ...
				newsess, ...
				thisassr, ...
				'Keys',{'project_id','subject_label','session_label'}, ...
				'MergeKeys', true, ...
				'Type','Full' ...
				);
		end
		
	end
	
	% Save the session assessor table to file
	disp('Writing session data to file')
	sess_detail_file = fullfile(out_dir, ...
		['detailed_report_sess_' timestamp '.csv']);
	writetable(newsess,sess_detail_file,'QuoteStrings',true)

end


% We're done
return
