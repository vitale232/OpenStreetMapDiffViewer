timeout 3
set OSGEO4W_ROOT=C:\OSGeo4W
set GDAL_DATA="D:\Program_Files\miniconda3\envs\osmdiff_viewer\Library\share\gdal"
set PROJ_LIB="D:\Program_Files\miniconda3\envs\osmdiff_viewer\Library\share\proj"
reg ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /f /d "%PATH%"
reg ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v GDAL_DATA /t REG_EXPAND_SZ /f /d "%GDAL_DATA%"
reg ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PROJ_LIB /t REG_EXPAND_SZ /f /d "%PROJ_LIB%"
timeout 10
