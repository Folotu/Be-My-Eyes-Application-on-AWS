// Get references to DOM elements
// Format
const boldButton = document.getElementById('bold');
const italicButton = document.getElementById('italic');
const underlineButton = document.getElementById('underline');
const strikethroughButton = document.getElementById('strikethrough');
const superscriptButton = document.getElementById('superscript');
const subscriptButton = document.getElementById('subscript');

// List
const orderedListButton = document.getElementById('insertOrderedList');
const unOrderedListButton = document.getElementById('insertUnorderedList');


// Alignment
const justifyLeftButton = document.getElementById('justifyLeft');
const justifyCenterButton = document.getElementById('justifyCenter');
const justifyRighttButton = document.getElementById('justifyRight');
const justifyFullButton = document.getElementById('justifyFull');


// Spacing
const indentButton = document.getElementById('indent');
const outdentButton = document.getElementById('outdent');

// Undo/Redo
const undoButton = document.getElementById('undo');
const redoButton = document.getElementById('redo');


// Link
document.getElementById('createLink').addEventListener('click', () => {
    let url = prompt('Enter the link URL');
    document.execCommand('createLink', false, url);
  });
  
  document.getElementById('unLink').addEventListener('click', () => {
    document.execCommand('unlink', false, null);  
  });


// Heading
const formatblock = document.getElementById('formatblock');

// font
const fontName = document.getElementById('fontName'); 
const fontSize = document.getElementById('fontSize');
const foreColor = document.getElementById('foreColor');
const backColor = document.getElementById('backColor');

// Content Editor
const editor = document.getElementById('text-input');


// ===============CLICK HANDLER===============

// Bold button click handler
boldButton.addEventListener('click', function() {
  document.execCommand('bold');
});

// Italic button click handler 
italicButton.addEventListener('click', function() {
  document.execCommand('italic'); 
});

underlineButton.addEventListener('click', function() {
  document.execCommand('underline'); 
});

strikethroughButton.addEventListener('click', function() {
  document.execCommand('strikethrough'); 
});

superscriptButton.addEventListener('click', function() {
  document.execCommand('superscript'); 
});

subscriptButton.addEventListener('click', function() {
  document.execCommand('subscript'); 
});


// List
orderedListButton.addEventListener('click', function() {
    document.execCommand('insertOrderedList'); 
  });

  unOrderedListButton.addEventListener('click', function() {
    document.execCommand('insertUnorderedList'); 
  });

//   Alignment
justifyLeftButton.addEventListener('click', function() {
    document.execCommand('justifyLeft'); 
  });

  justifyCenterButton.addEventListener('click', function() {
    document.execCommand('justifyCenter'); 
  });

  justifyRighttButton.addEventListener('click', function() {
    document.execCommand('justifyRight'); 
  });

  justifyFullButton.addEventListener('click', function() {
    document.execCommand('justifyFull'); 
  });


//   Spacing
indentButton.addEventListener('click', function() {
    document.execCommand('indent'); 
  });

  outdentButton.addEventListener('click', function() {
    document.execCommand('outdent'); 
  });


//   Undo/Redo
undoButton.addEventListener('click', function() {
    document.execCommand('undo'); 
  });
  redoButton.addEventListener('click', function() {
    document.execCommand('redo'); 
  });


//   Heading
  formatblock.addEventListener('change', function() {
    document.execCommand('formatBlock', false, this.value);
  });
  
//   Font
  fontName.addEventListener('change', function() {
    document.execCommand('fontName', false, this.value);  
  });
  
  fontSize.addEventListener('change', function() {
    document.execCommand('fontSize', false, this.value);
  });
  
  foreColor.addEventListener('change', function() {
    document.execCommand('foreColor', false, this.value); 
  });
  
  backColor.addEventListener('change', function() {
    document.execCommand('hiliteColor', false, this.value);
  });
