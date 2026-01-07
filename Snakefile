# Snakefile

import yaml
import os
import pandas as pd

configfile: "config.yaml"

# Use configured working directory
directory = config["directory"]

# Define output image and segmentation paths
input_tiff_basename = os.path.splitext(os.path.basename(config["INPUT_TIFF"]))[0]
image_output = os.path.join(directory, f"{input_tiff_basename}_STAT3D.tif")
seg_npy_output = os.path.join(directory, f"{input_tiff_basename}_STAT3D_seg.npy")

# Define CSV measurement paths
csv_QuPath_output = os.path.join(directory, "QuPath_measurements.csv")
average_min_distance_csv = os.path.join(directory, "average_min_distance.csv")
average_nuclear_expansion_csv = os.path.join(directory, "average_nuclear_expansion.csv")
nuclei_diameter_csv = os.path.join(directory, "nuclei_diameter.csv")
z_slice_csv = os.path.join(directory, "z_slice_measurements.csv")
export_dir = os.path.join(directory, "export")
Laplacian_score_csv = os.path.join(directory, "Laplacian_score.csv")

# Paths for cell-feature-matrix and Seurat outputs
matrix_gz = os.path.join(directory, "matrix.mtx.gz")
features_gz = os.path.join(directory, "features.tsv.gz")
barcodes_gz = os.path.join(directory, "barcodes.tsv.gz")

QC_pdf = os.path.join(directory, "QC.pdf")
sp_obj_rds = os.path.join(directory, "sp_obj.rds")
spatialobj_plot_pdf = os.path.join(directory, "spatialobj_plot.pdf")
singler_rds = os.path.join(directory, "singler.rds")
Spatial_SingleR_pdf = os.path.join(directory, "Spatial_SingleR.pdf")
UMAP_SingleR_pdf = os.path.join(directory, "UMAP_SingleR.pdf")
QC_predictions_pdf = os.path.join(directory, "SingleR_predictions_QC.pdf")

# Validate celldex reference
VALID_REFS = [
    "HumanPrimaryCellAtlasData",
    "BlueprintEncodeData",
    "DatabaseImmuneCellExpressionData",
    "MonacoImmuneData",
    "NovershternHematopoieticData",
    "MouseRNAseqData"
]

if config["ref"] not in VALID_REFS:
    raise ValueError(f"Invalid reference: {config['ref']}. Must be one of {VALID_REFS}")

# ----------------------
# Rule all
# ----------------------
rule all:
    input:
        Laplacian_score_csv,
        image_output,
        csv_QuPath_output,
        average_min_distance_csv,
        average_nuclear_expansion_csv,
        nuclei_diameter_csv,
        z_slice_csv,
        seg_npy_output,
        matrix_gz,
        features_gz,
        barcodes_gz,
        QC_pdf,
        sp_obj_rds,
        spatialobj_plot_pdf,
        singler_rds,
        Spatial_SingleR_pdf,
        UMAP_SingleR_pdf,
        QC_predictions_pdf

# ----------------------
# QuPath Z-slice rules
# ----------------------
rule generate_zslice_groovy:
    output: "Z_slice_script.groovy"
    params:
        z_slice_csv=z_slice_csv,
        export_dir=export_dir
    run:
        with open(output[0], "w") as f:
            f.write(f"""// Z_slice_script.groovy
import qupath.lib.regions.RegionRequest
QP.createAllFullImageAnnotations(true)
def hierarchy = getCurrentHierarchy()
def z_slice_csv = "{params.z_slice_csv}"
saveAnnotationMeasurements(z_slice_csv)
double downsample = 1.0
def dir = buildFilePath("{params.export_dir}")
mkdirs(dir)
def server = getCurrentServer()
def annotations = getAnnotationObjects()
for (def annotation in annotations) {{
    def request = RegionRequest.createInstance(server.getPath(), downsample, annotation.getROI())
    def name = getCurrentImageNameWithoutExtension()
    def outputName = "${{name}}-${{request.x}}_${{request.y}}_${{request.width}}x${{request.height}}_${{request.z}}.tif"
    def path = buildFilePath(dir, outputName)
    writeImageRegion(server, request, path)
}}
print "Done!"
""")

rule run_zslice_script:
    input:
        image=config["INPUT_TIFF"],
        script="Z_slice_script.groovy"
    output:
        zslice = z_slice_csv
    shell:
        "QuPath script --image {input.image} {input.script}"

# ----------------------
# Laplacian
# ----------------------
rule compute_laplacian:
    input:
        tiff=config["INPUT_TIFF"]
    output:
        csv=Laplacian_score_csv
    shell:
        "python scripts/Laplacian_score_script.py {input.tiff} {output.csv}"

# ----------------------
# TIFF processing
# ----------------------
rule process_tiff:
    input:
        tiff=config["INPUT_TIFF"],
        csv=Laplacian_score_csv
    output:
        image_output
    run:
        import subprocess
        import pandas as pd
        df = pd.read_csv(input.csv)
        df_sorted = df.sort_values(by=df.columns[1], ascending=False)
        default_z_b = int(df_sorted.iloc[0, 0])
        default_z_a = int(df_sorted.iloc[1, 0]) if len(df_sorted) > 1 else int(df_sorted.iloc[0, 0])
        z_a = config.get("Z_SLICE_A", default_z_a)
        z_b = config.get("Z_SLICE_B", default_z_b)
        subprocess.run([
            "python", "scripts/process_tiff.py",
            input.tiff, str(z_a), str(z_b), str(config["LEVEL"]), output[0]
        ])

# ----------------------
# QuPath measurements
# ----------------------
rule generate_groovy_script:
    output: "QuPath_script.groovy"
    run:
        with open(output[0], "w") as f:
            f.write(f"""// QuPath_script.groovy
setImageType('FLUORESCENCE')
createFullImageAnnotation(true)
runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{{"detectionImage":"Channel 1","backgroundByReconstruction":true,"backgroundRadius":{config["BACKGROUND_RADIUS"]},"medianRadius":{config["MEDIAN_RADIUS"]},"sigma":{config["SIGMA"]},"minArea":{config["MIN_AREA"]},"maxArea":{config["MAX_AREA"]},"threshold":{config["THRESHOLD"]},"watershedPostProcess":true,"cellExpansion":{config["CELL_EXPANSION"]},"includeNuclei":true,"smoothBoundaries":true,"makeMeasurements":true}}')
saveDetectionMeasurements('{csv_QuPath_output}')
""")

rule run_qupath_analysis:
    input:
        image=image_output,
        script="QuPath_script.groovy"
    output:
        csv_QuPath_output
    shell:
        "QuPath script --image {input.image} {input.script}"

rule image_measurements:
    input:
        csv=csv_QuPath_output
    output:
        min_distance=average_min_distance_csv,
        nuclear_expansion=average_nuclear_expansion_csv,
        nuclei_diameter=nuclei_diameter_csv
    shell:
        "Rscript scripts/image_measurements.R {input.csv} {output.min_distance} {output.nuclear_expansion} {output.nuclei_diameter}"

# ----------------------
# Cellpose
# ----------------------
rule run_cellpose:
    input:
        image=image_output,
        diameter_csv=nuclei_diameter_csv
    output:
        seg_npy=seg_npy_output
    params:
        diameter=lambda wildcards, input: pd.read_csv(input.diameter_csv)["Average_Diameter"].iloc[0],
        use_gpu="--use_gpu" if config["cellpose_use_gpu"] else "",
        do_3D="--do_3D" if config.get("cellpose_do_3D", False) else ""
    shell:
        """
        python -m cellpose \
            --dir {config[directory]} \
            --pretrained_model nuclei \
            --chan 0 \
            --chan2 0 \
            --img_filter {config[cellpose_img_filter]} \
            --diameter {params.diameter} \
            {params.do_3D} \
            --save_tif \
            --verbose \
            {params.use_gpu}
        """

# ----------------------
# Cell-to-transcript
# ----------------------
rule cell_to_transcript:
    input:
        seg_data=seg_npy_output,
        transcripts=config["transcripts_df"],
        average_nuclear_expansion_csv=average_nuclear_expansion_csv
    output:
        matrix=matrix_gz.replace(".gz",""),
        features=features_gz.replace(".gz",""),
        barcodes=barcodes_gz.replace(".gz","")
    params:
        pixel_size=config["PIXEL_SIZE"],
        z_slice_micron=config["Z_SLICE_MICRON"],
        nuc_exp_pixel=lambda wildcards, input: (
            pd.read_csv(input.average_nuclear_expansion_csv)["Average_Nuclear_Expansion"].iloc[0]
            / config["PIXEL_SIZE"]
        ),
        nuc_exp_slice=lambda wildcards, input: (
            pd.read_csv(input.average_nuclear_expansion_csv)["Average_Nuclear_Expansion"].iloc[0]
            / config["Z_SLICE_MICRON"]
        )
    script:
        "scripts/cell_to_transcript.py" if config.get("cellpose_do_3D", False)
        else "scripts/cell_to_transcript_2D.py"


# ----------------------
# Gzip outputs
# ----------------------
rule gzip_outputs:
    input:
        matrix=rules.cell_to_transcript.output.matrix,
        features=rules.cell_to_transcript.output.features,
        barcodes=rules.cell_to_transcript.output.barcodes
    output:
        matrix_gz=matrix_gz,
        features_gz=features_gz,
        barcodes_gz=barcodes_gz
    shell:
        """
        gzip -c {input.matrix} > {output.matrix_gz}
        gzip -c {input.features} > {output.features_gz}
        gzip -c {input.barcodes} > {output.barcodes_gz}
        """

# ----------------------
# Seurat spatial object
# ----------------------
rule seurat_spatial_object_automatic_annotation:
    input:
        input_dir=config["directory"],
        barcodes=barcodes_gz
    output:
        rds=sp_obj_rds,
        pdf=spatialobj_plot_pdf,
        rds_singler=singler_rds,
        pdf_umap_singler=UMAP_SingleR_pdf,
        pdf_spatial_singler=Spatial_SingleR_pdf,
        pdf_qc=QC_pdf,
        pdf_qc_predictions=QC_predictions_pdf
    params:
        ref=config["ref"],
        label_column=config["label_column"]
    script:
        "scripts/seurat_spatial_object.R" if config.get("cellpose_do_3D", False) \
        else "scripts/seurat_spatial_object_2D.R"
