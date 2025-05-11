//maybe add setImageType('FLUORESCENCE') in the beginning;
createFullImageAnnotation(true)
runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{"detectionImage":"Channel 1","backgroundByReconstruction":true,"backgroundRadius":10.0,"medianRadius":0.0,"sigma":1.0,"minArea":10.0,"maxArea":1000.0,"threshold":30.0,"watershedPostProcess":true,"cellExpansion":2.0,"includeNuclei":true,"smoothBoundaries":true,"makeMeasurements":true}')
