window.onload  = function() {
    // Extract sessionId from URL query parameters
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('sessionId');
    
    if (sessionId) {
        // Store the session ID in local storage
        localStorage.setItem('sessionId', sessionId);
        
        // Remove sessionId from URL for cleanliness
        history.replaceState(null, null, window.location.pathname);
    // } else {
    //     // Redirect to landing page if sessionId is not found
    //     window.location.href = landingPageUrl;
    }
};

function navigateWithSession(event, url) {
    event.preventDefault(); // Prevent the default link behavior
    const sessionId = localStorage.getItem('sessionId');
    if (sessionId) {
        window.location.href = url + '?sessionId=' + sessionId;
    } else {
        window.location.href = url; // Navigate without session ID if not found
    }
}
