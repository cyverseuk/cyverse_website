# CyVerseUK web app

This code is deployed at <a href="https://cyverseuk.herokuapp.com/">cyverseuk.herokuapp.com</a>.  
It doesn't represent an alternative to the <a href="https://de.cyverse.org/de/">Discovery Environment</a>, but provides a fast and easy way to use the applications hosted at the <a href="http://www.earlham.ac.uk/">Earlham Institute</a>.  

### Important warning

The EI storage system is **not** public yet, so you will need to ask permission to the team (you can use the contact form) to be able to run jobs from this website (as it will archive the output on our system).

##### What the web app provides...

The web application provides a fast way to access and use CyVerseUK resources hosted at EI.  
It will authenticate the user with OAuth2 against CyVerse, so you will not need a new username or password.  
You will be able to submit multiple files during the job submission (if it's allowed by the app) (_this is an open ticket in the DE for Agave applications_), both uploading from your local machine or importing them from a comma separated list of URLs.  
Your output files will be archived on the EI storage system and you will be able to preview and download your files from the website, as well as downloading a `.tar` archive of the whole job.

##### ...and what it doesn't

As said, this website is not meant to be a complete Discovery Environment. You will not be able to delete or change permissions to your file from here (you will have to use the command line tool), nor to browse shared files or applications.

**Please report any bug or error you may find!**
