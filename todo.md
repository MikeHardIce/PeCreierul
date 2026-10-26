
# TODO

## EditScreen
- fix import parsing bug "Would Should.csv" (done, actually was the export)
- fix scrolling and display bug when edit screen list is too large (done)
- enable renaming of lesson (done)
- have answer hints to the questions (done)
    - import/export (done)
- use wikipedia to import images as "questions" for a lesson
    - based on a list of keywords "answers" the user has chosen
    - add a note and a link to the license section
    - use the "extract" in the json response as hint (replace the occurence of the keyword with stars, remove html tags)
    - example GET https://en.wikipedia.org/api/rest_v1/page/summary/Stegosaurus (don't forget to url encode the keyword)
- tab should jump to the next input element
- remove "delete of tags" button if they are still being used (global)
- implement multiple correct answers (maybe ; separator)

## MenuScreen
- show number of vocabularies/entries contained in the lesson boxes (done)
- implement import/export for entire lessons
- multi select lessons for training, where it takes a selection of lesson terms of each lesson

## TraininScreen
- fix when finishing a lesson and starting a new one, the text box is still locked (done)
- support image display if question contains a path to an image (done)
- display answer hint by holding "alt" (done)
- indicate that the lesson is over when it's over
- implement multiple choice (training object already supports it, maybe chose mode when starting a lesson)
- maybe settings for stack sizes and number of stacks when starting a lesson

## General
- clean up code once settled
- improve the look