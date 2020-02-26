set GAMES_PATH=c:\users\raysm\GamesDemo
set PROJ_MODULE=dots
set PROJ_PATH=%GAMES_PATH%\%PROJ_MODULE
set COMPILER=C:\ProgramData\Anaconda3\envs\py36
set RESOURCE_LIB=%GAMES_PATH%\resource_lib\src
set PYTHONPATH=%PYTHONPATH%;%RESOURCE_LIB%
%COMPILER%\python src\crs_dots.py ^
  --trace execute,keycmd,execute_part_change,show_move ^
  --show_score=False --stroke_move=False --playing=G,Ax,Av,D
