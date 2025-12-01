// Z_slice_script.groovy
import qupath.lib.regions.RegionRequest

// Create full-image annotations
QP.createAllFullImageAnnotations(true)
def hierarchy = getCurrentHierarchy()

// Save measurements
def z_slice_csv = "z_slice_measurements.csv"
saveAnnotationMeasurements(z_slice_csv)

// Export images for each annotation
double downsample = 1.0
def dir = buildFilePath("/stat3d/export")
mkdirs(dir)

def server = getCurrentServer()
def annotations = getAnnotationObjects()
println annotations

for (def annotation in annotations) {
    def request = RegionRequest.createInstance(
        server.getPath(),
        downsample,
        annotation.getROI()
    )
    println annotation.getROI().getZ()
    def name = getCurrentImageNameWithoutExtension()
    def outputName = "${name}-${request.x}_${request.y}_${request.width}x${request.height}_${request.z}.tif"
    def path = buildFilePath(dir, outputName)
    println path
    writeImageRegion(server, request, path)
}
print "Done!"
