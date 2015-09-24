//==================================================
// slide object
//==================================================
function slideImg(src,link,txt,target,attr) {
  // s = new slideImg();

  // Image URL
  this.src = src;

  // Link URL
  this.link = link;
  
  //Alt text for the image
  this.text = txt;

  // Name of the target window ("_blank")
  this.target = target;

  // Custom duration for the slide, in milliseconds.
  // This is an optional parameter.
  // this.timeout = 3000

  // Attributes for the target window:
  // width=n,height=n,resizable=yes or no,scrollbars=yes or no,
  // toolbar=yes or no,location=yes or no,directories=yes or no,
  // status=yes or no,menubar=yes or no,copyhistory=yes or no
  // Example: "width=200,height=300"
  this.attr = attr;

  // Create an image object for the slide
  if (document.images) {
    this.image = new Image();
  }

  // Flag to tell when load() has already been called
  this.loaded = false;

  //--------------------------------------------------
  this.load = function() {
    // This method loads the image for the slide

    if (!document.images) { return; }

    if (!this.loaded) {
      this.image.src = this.src;
	  this.image.alt = this.text;
      this.loaded = true;
    }
  }

  //--------------------------------------------------
  this.hotlink = function() {
    // This method jumps to the slide's link.
    // If a window was specified for the slide, then it opens a new window.
    var mywindow;

    // If this slide does not have a link, do nothing
    if (!this.link) return;

    // Open the link in a separate window?
    if (this.target) {

      // If window attributes are specified,
      // use them to open the new window
      if (this.attr) {
        mywindow = window.open(this.link, this.target, this.attr);

      } else {
        // If window attributes are not specified, do not use them
        // (this will copy the attributes from the originating window)
        mywindow = window.open(this.link, this.target);
      }

      // Pop the window to the front
      if (mywindow && mywindow.focus) mywindow.focus();

    } else {
      // Open the link in the current window
      location.href = this.link;
    }
  }
}

//==================================================
// slideshow object
//==================================================
function slideshow( slideshowname ) {
  // ss = new slideshow("ss");

  // Name of this object
  // (required if you want your slideshow to auto-play)
  // For example, "SLIDES1"
  this.name = slideshowname;

  // When we reach the last slide, should we loop around to start the
  // slideshow again?
  this.repeat = true;

  // Number of images to pre-fetch.
  // -1 = preload all images.
  //  0 = load each image is it is used.
  //  n = pre-fetch n images ahead of the current image.
  // I recommend preloading all images unless you have large
  // images, or a large amount of images.
  this.prefetch = -1;

  // IMAGE element on your HTML page.
  // For example, document.images.SLIDES1IMG
  this.image;

  // ID of a DIV element on your HTML page that will contain the text.
  // For example, "slides2text"
  // Note: after you set this variable, you should call
  // the update() method to update the slideshow display.
  this.textid;

  // Milliseconds to pause between slides.
  // Individual slides can override this.
  this.timeout = 3000;

  // Hook functions to be called before and after updating the slide
  // this.pre_update_hook = function() { }
  // this.post_update_hook = function() { }

  // These are private variables
  this.slides = new Array();
  this.current = 0;
  this.timeoutid = 0;

  //--------------------------------------------------
  // Public methods
  //--------------------------------------------------
  this.add_slide = function(slide) {
    // Add a slide to the slideshow.
    // For example:
    // SLIDES1.add_slide(new slide("s1.jpg", "link.html"))

    var i = this.slides.length;

    // Prefetch the slide image if necessary
    if (this.prefetch == -1) {
      slide.load();
    }

    this.slides[i] = slide;
  }

  //--------------------------------------------------
  this.play = function(timeout) {
    // This method implements the automatically running slideshow.
    // If you specify the "timeout" argument, then a new default
    // timeout will be set for the slideshow.

    // Make sure we're not already playing
    this.pause();

    // If the timeout argument was specified (optional)
    // then make it the new default
    if (timeout) {
      this.timeout = timeout;
    }

    // If the current slide has a custom timeout, use it;
    // otherwise use the default timeout
    if (typeof this.slides[ this.current ].timeout != 'undefined') {
      timeout = this.slides[ this.current ].timeout;
    } else {
      timeout = this.timeout;
    }

    // After the timeout, call this.loop()
    this.timeoutid = setTimeout( this.name + ".loop()", timeout);
  }
   
//--------------------------------------------------
  this.playPause = function(id) {
    // This method implements the automatically running slideshow.
    // If you specify the "timeout" argument, then a new default
    // timeout will be set for the slideshow.

	if (document.getElementById(id).value == "Pause") {
		document.getElementById(id).value = "Play ";
		clearTimeout(this.timeoutid);
		this.timeoutid = 0;
	} else {
		this.next();
		
		document.getElementById(id).value = "Pause";

		clearTimeout(this.timeoutid);
		this.timeoutid = 0;

		// If the current slide has a custom timeout, use it;
		// otherwise use the default timeout
		if (typeof this.slides[ this.current ].timeout != 'undefined') {
			timeout = this.slides[ this.current ].timeout;
		} else {
			timeout = this.timeout;
		}

		// After the timeout, call this.loop()
		this.timeoutid = setTimeout( this.name + ".loop()", timeout);
	}
  }

  //--------------------------------------------------
  this.pause = function() {
    // This method stops the slideshow if it is automatically running.

    if (this.timeoutid != 0) {

      clearTimeout(this.timeoutid);
      this.timeoutid = 0;

    }
  }

  //--------------------------------------------------
  this.update = function() {
    // This method updates the slideshow image on the page

    // Make sure the slideshow has been initialized correctly
    if (! this.valid_image()) { return; }


    // Convenience variable for the current slide
    var slide = this.slides[ this.current ];

    // Load the slide image if necessary
    slide.load();

    // Update the image.
    this.image.src = slide.image.src;
	this.image.alt = slide.text;
	this.image.title = slide.text;

    // Call the post-update hook function if one was specified
    if (typeof this.post_update_hook == 'function') {
      this.post_update_hook();
    }

    // Do we need to pre-fetch images?
    if (this.prefetch > 0) {

      var next, prev, count;

      // Pre-fetch the next slide image(s)
      next = this.current;
      prev = this.current;
      count = 0;
      do {

        // Get the next and previous slide number
        // Loop past the ends of the slideshow if necessary
        if (++next >= this.slides.length) next = 0;
        if (--prev < 0) prev = this.slides.length - 1;

        // Preload the slide image
        this.slides[next].load();
        this.slides[prev].load();

        // Keep going until we have fetched
        // the designated number of slides

      } while (++count < this.prefetch);
    }
  }

  //--------------------------------------------------
  this.goto_slide = function(n) {
    // This method jumpts to the slide number you specify.
    // If you use slide number -1, then it jumps to the last slide.
    // You can use this to make links that go to a specific slide,
    // or to go to the beginning or end of the slideshow.
    // Examples:
    // onClick="myslides.goto_slide(0)"
    // onClick="myslides.goto_slide(-1)"
    // onClick="myslides.goto_slide(5)"

    if (n == -1) {
      n = this.slides.length - 1;
    }

    if (n < this.slides.length && n >= 0) {
      this.current = n;
    }

    this.update();
  }

  //--------------------------------------------------
  this.next = function() {
    // This method advances to the next slide.

    // Increment the image number
    if (this.current < this.slides.length - 1) {
      this.current++;
    } else if (this.repeat) {
      this.current = 0;
    }

    this.update();
  }


  //--------------------------------------------------
  this.previous = function() {
    // This method goes to the previous slide.

    // Decrement the image number
    if (this.current > 0) {
      this.current--;
    } else if (this.repeat) {
      this.current = this.slides.length - 1;
    }

    this.update();
  }

  //--------------------------------------------------
  this.zoomUp = function() {
    // This method increments the image height by 50
    var oldHeight = this.image.height;
    this.image.height = oldHeight + 50;		
    this.update();
  }

  //--------------------------------------------------
  this.zoomDown = function() {
    // This method increments the image height by 50
    var oldHeight = this.image.height;
    this.image.height = oldHeight - 50;		
    this.update();
  }

  //--------------------------------------------------
  this.get_text = function() {
    // This method returns the text of the current slide

    return(this.slides[ this.current ].text);
  }

  //--------------------------------------------------
  this.hotlink = function() {
    // This method calls the hotlink() method for the current slide.

    this.slides[ this.current ].hotlink();
  }

//--------------------------------------------------
  this.loop = function() {
    // This method is for internal use only.
    // This method gets called automatically by a JavaScript timeout.
    // It advances to the next slide, then sets the next timeout.
    // If the next slide image has not completed loading yet,
    // then do not advance to the next slide yet.

    // Make sure the next slide image has finished loading
    if (this.current < this.slides.length - 1) {
      next_slide = this.slides[this.current + 1];
      if (next_slide.image.complete == null || next_slide.image.complete) {
        this.next();
      }
    } else { // we're at the last slide
      this.next();
    }

    // Keep playing the slideshow
    this.play( );
  }


  //--------------------------------------------------
  this.valid_image = function() {
    // Returns 1 if a valid image has been set for the slideshow

    if (!this.image)
    {
      return false;
    }
    else {
      return true;
    }
  }

  //--------------------------------------------------
  this.getElementById = function(element_id) {
    // This method returns the element corresponding to the id

    if (document.getElementById) {
      return document.getElementById(element_id);
    }
    else if (document.all) {
      return document.all[element_id];
    }
    else if (document.layers) {
      return document.layers[element_id];
    } else {
      return undefined;
    }
  }
 }
  
