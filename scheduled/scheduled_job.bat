call D:\Program_Files\miniconda3\condabin\activate.bat osmdiff_viewer
python D:\OpenStreetMap\OpenStreetMapDiffViewer\scheduled\scheduled_job.py
timeout 10
call conda deactivate
