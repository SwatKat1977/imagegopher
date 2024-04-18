# image Gopher

Image Gopher is a service to organise, index and tag your images.

Note: This code is based on my original project from 2018 (imagedexer), which I have since deleted.

# Developer Information

## Services

Image Gopher currently consists of 2 microservices:

Note: More then 2 are listed, if they are marked as {FUTURE} then they haven't been started yet!

### gatherer
Scans directories for images and collates them.

### burrow
Main processing microservice that orchestrates and manages images and tags.

### webhost {FUTURE}
Web server for the user to manage images, tags and configuration.

## Development Roadmap

The project is in early alpha, currently the main focus is getting file indexing working.

Todo list:
* Generate thumbnails of images
* Create a web interface to support viewing / managing of images
* Dockerfy the microservices
* Flag up duplicate images
* Optimise file scanning
* Report image statistics
* Extract EXIFF data (where they exist)