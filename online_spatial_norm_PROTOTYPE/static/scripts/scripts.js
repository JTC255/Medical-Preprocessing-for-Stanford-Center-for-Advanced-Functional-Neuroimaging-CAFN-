function displayFileNames() {
    var input = document.getElementById('file-upload-form');
    var output = document.getElementById('file-upload');
    output.innerHTML = ''; // Clear the previous content

    console.log('Number of files selected:', input.files.length);
    
    for (var i = 0; i < input.files.length; i++) {
        var file = input.files[i];
        var listItem = document.createElement('div');
        
        listItem.classList.add('file-item');
        
        listItem.textContent = file.name;
        output.appendChild(listItem);
    }
}

function triggerFileUpload() {
    document.getElementById('file-upload').click();
}

function checkAndSubmit() {
    //does nothing, kind of just a placeholder function
    document.getElementById('file-upload-form').submit();
  
}

function updateProgressBar(metric) {
    // Ensure metric is within the range 0 to 100
    if (metric < 0) metric = 0;
    if (metric > 100) metric = 100;

    // Select the progress bar element
    var progressBar = document.getElementById('progress-bar');

    // Update the width of the progress bar based on the metric
    if (metric === 0) {
           progressBar.style.display = 'none';  // Hide the progress bar
   } else {
       progressBar.style.display = 'block';  // Show the progress bar
       progressBar.style.width = metric + '%';  // Update the width
   }
}

// Example usage: Set the progress bar to 70% based on a custom metric
updateProgressBar(0);

var c = 0;
var up = true;

// Create a function to run the loop with a delay
function animateProgressBar() {
    if (c < 100 && up === true) {
        c += 1;
    } else if (c >= 100 && up === true) {
        up = false;
    }
    
    if (up === false && c > 0) {
        c -= 1;
    } else if (up === false && c <= 0) {
        up = true;
    }
    
    updateProgressBar(c);

    // Continue the animation with a delay
    setTimeout(animateProgressBar, 25); // Adjust delay as needed
}


function validate_norm_form() {
    var fileInput = document.getElementById('files-uploaded');
    console.log("HAHA")
    if (fileInput.files.length === 0) {
        alert("Please upload at least one file to proceed");
        return false; //prevent submission
    }
    return true;
}



let currentIndex = 0;

function slide(direction) {
    const slides = document.querySelectorAll('.gallery-slide img');
    const totalSlides = slides.length;

    currentIndex += direction;

    if (currentIndex < 0) {
        currentIndex = totalSlides - 1;
    } else if (currentIndex >= totalSlides) {
        currentIndex = 0;
    }

    // Deselect all images
    slides.forEach(img => img.classList.remove('selected'));

    // Select the current image
    slides[currentIndex].classList.add('selected');

    // Calculate the offset to center the selected image
    const galleryContainer = document.querySelector('.gallery-container');
    const slideContainer = document.querySelector('.gallery-slide');
    const selectedImage = slides[currentIndex];
    const containerWidth = slideContainer.offsetWidth;
    const imageWidth = selectedImage.offsetWidth;

    const offset = selectedImage.offsetLeft + 10  + (imageWidth - containerWidth)/2 ; //the ten is image gap in gallery-container
    console.log("CONTAINER WIDTH:")
    console.log(containerWidth)
    console.log("offset:")
    console.log(selectedImage.offsetLeft)
    console.log("image width")
    console.log(imageWidth)
    

    slideContainer.style.transform = `translateX(${-offset}px)`;
}
// Initial selection of the first image
document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.gallery-slide img');
    slides[currentIndex].classList.add('selected');

    // Center the first image initially
    const galleryContainer = document.querySelector('.gallery-container');
    const slideContainer = document.querySelector('.gallery-slide');
    const selectedImage = slides[currentIndex];
    const containerWidth = galleryContainer.offsetWidth;
    const imageWidth = selectedImage.offsetWidth;

    const offset = selectedImage.offsetLeft + 10 + imageWidth / 2 - containerWidth / 2;
    console.log("CONTAINER WIDTH:")
    console.log(containerWidth)
    console.log("offset:")
    console.log(selectedImage.offsetLeft)
    console.log("image width")
    console.log(imageWidth)

    slideContainer.style.transform = `translateX(${-offset}px)`;
});


// Start the animation
//animateProgressBar();

let lastScrollTime = 0;
const throttleDelay = 200;

document.querySelector('.gallery-container').addEventListener('wheel', function(event) {
    event.preventDefault();
    const currentTime = new Date().getTime();

    if (currentTime - lastScrollTime >= throttleDelay) {
        lastScrollTime = currentTime;
        
        if (event.deltaY > 0) {
            slide(1); // Scroll down/right, go to the next slice
        } else {
            slide(-1); // Scroll up/left, go to the previous slice
        }
        
        event.preventDefault(); // Prevent the default scroll behavior
    }
});
