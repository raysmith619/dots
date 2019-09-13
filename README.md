# dots
Dots (complete the squares) Game

In addition to making a fun game, our goal is to develop / demonstrate machine learning.  Initially we plan to produce a game playing platform which facilitates the automated playing of many games, producing a collection of game results upon which machine learning can learn how to play the game effectively.

## The Dots game:
I appologize if others have a different game in mind.  The following is the game as I've seen and played it.
The playing board is created by creating a rectangular array of dots, the connection of adjacent dots create squares.  A 10 by 10 grid is created by 11 dots accross and 11 dots down, providing, upon completion an array of 10 columns of squares horrizontaly by 10 rows of squares vertically.  Please open the file "dots_screen_shots.docx" for a quick view of the game in action.

The game is usually played by two players with alternating moves.  Each move consists of creating a new horizontal or vertical line connecting adjacent dots.  When a player completes one or two squares with their move, they mark the completed square(s) and must take an and additional move.  When all the squares created, the game is completed.  It is considered a win for the player if their number of squares created exceeds their opponent.  If the number of squares of both players is identical it is a tie game.

## Running the game:
The game is started by executing "python crs_dots.py" in the "src" directory.  The setup of the game windows and settings is specified by the crs_dots.properties file.

## Processing game results:
Executing the game creates a new results file, usually stored in the "../gmres" or "../test_gmres" directory.  Examples of results files can be found in the "test_gmres" directory.

### Example Game Results File:
```
# c:\Users\raysm\workspace\python\crs_dots\gmres\dotsgame_20190905_125457.gmres
# On: September 05, 2019


version("ver01_rel01")
game(name="dots", nplayer=2, nrow=2, ncol=2, nmove=12, ts="20190905_125457")
moves([(1,1,3), (2,2,2), (1,1,1), (2,2,1), (1,2,1), (2,2,3), (1,1,2),
(2,1,1), (2,1,2), (2,3,1), (1,2,2), (1,3,2)])
results((1,2), (2,2))

game(name="dots", nplayer=2, nrow=2, ncol=2, nmove=12, ts="20190905_125458")
moves([(1,1,2), (2,2,3), (1,1,2), (2,1,1), (1,2,2), (2,2,1), (1,2,1),
(2,1,1), (2,3,1), (2,2,2), (1,1,3), (1,3,2)])
results((1,2), (2,2))
```

Loading and simple analysis of game results files is done by executing "crs_dots_load.py" in the "src" directory.

## Example crs_dots_load.py output:
```
 Creating Log File Name: C:\Users\raysm\workspace\python\crs_dots\log\crs_dots_load_20190905_130004.sllog
 loadTraceFlags: game_results,game,adding_list,SkipFile
 crs_dots_load.py --results_dir=../test_gmres

 args: Namespace(ncol=None, nrow=None, results_dir='../test_gmres', results_files=True, test_file=None, trace='')

 Files loaded from directory: ../test_gmres
 End loading file ../test_gmres\dotsgame_20190903_172541.gmres     ngame=1280 nrow=6 ncol=6
 End loading file ../test_gmres\dotsgame_20190904_101744.gmres     ngame=4 nrow=6 ncol=6
 End loading file ../test_gmres\dotsgame_20190904_104735.gmres     ngame=2 nrow=20 ncol=20
 End loading file ../test_gmres\dotsgame_20190904_105054.gmres     ngame=95 nrow=20 ncol=20
 End loading file ../test_gmres\dotsgame_20190904_123154.gmres     ngame=434 nrow=10 ncol=10
 End loading file ../test_gmres\dotsgame_20190904_140326.gmres     ngame=122 nrow=10 ncol=10
 End loading file ../test_gmres\dotsgame_20190904_143304.gmres     ngame=701 nrow=10 ncol=10
 End loading file ../test_gmres\dotsgame_20190904_201625.gmres     ngame=262 nrow=15 ncol=15
 End loading file ../test_gmres\dotsgame_20190904_231003.gmres     ngame=1349 nrow=15 ncol=15
 End loading file ../test_gmres\dotsgame_20190905_105059.gmres     ngame=23 nrow=7 ncol=7
 End loading file ../test_gmres\dotsgame_20190905_105743.gmres     ngame=985 nrow=7 ncol=7
 End loading file ../test_gmres\dotsgame_20190905_125457.gmres     ngame=206 nrow=2 ncol=2
 End loading 12 files
 5463 games in 12 files
  Game Statistics by number of rows, cols
 rows cols Games
    2    2   206
    6    6  1284
    7    7  1008
   10   10  1257
   15   15  1611
   20   20    97
  Detailed Game Statistics by number of rows, cols
 rows cols games  pl   win(%   ) [(%sqs)]  loss(%   ) [(%sqs)]  tie (%   ) [(%sqs)]  
    2    2   206   1    80(38.8) [(91.9)]   59(28.6) [( 8.9)]   67(32.5) [(50.0)]
    2    2   206   2    59(28.6) [(91.1)]   80(38.8) [( 8.1)]   67(32.5) [(50.0)]
 ----------------------------------------------------------------------
    6    6  1284   1   623(48.5) [(62.8)]  568(44.2) [(37.2)]   93( 7.2) [(50.0)]
    6    6  1284   2   568(44.2) [(62.8)]  623(48.5) [(37.2)]   93( 7.2) [(50.0)]
 ----------------------------------------------------------------------
    7    7  1008   1   524(52.0) [(60.8)]  484(48.0) [(40.1)]    0( 0.0) [( 0.0)]
    7    7  1008   2   484(48.0) [(59.9)]  524(52.0) [(39.2)]    0( 0.0) [( 0.0)]
 ----------------------------------------------------------------------
   10   10  1257   1   593(47.2) [(58.4)]  611(48.6) [(41.3)]   53( 4.2) [(50.0)]
   10   10  1257   2   611(48.6) [(58.7)]  593(47.2) [(41.6)]   53( 4.2) [(50.0)]
 ----------------------------------------------------------------------
   15   15  1611   1   826(51.3) [(55.9)]  785(48.7) [(44.3)]    0( 0.0) [( 0.0)]
   15   15  1611   2   785(48.7) [(55.7)]  826(51.3) [(44.1)]    0( 0.0) [( 0.0)]
 ----------------------------------------------------------------------
   20   20    97   1    54(55.7) [(54.7)]   42(43.3) [(45.0)]    1( 1.0) [(50.0)]
   20   20    97   2    42(43.3) [(55.0)]   54(55.7) [(45.3)]    1( 1.0) [(50.0)]
 ----------------------------------------------------------------------
 Saving properties file C:\Users\raysm\workspace\python\crs_dots\crs_dots_load.properties
 Closing log file C:\Users\raysm\workspace\python\crs_dots\log\crs_dots_load_20190905_130004.sllog
```

###Example of an updated results loading output
Note that we show more game stats in the loading.
```
 20190912_212756 Creating Log File Name: C:\Users\raysm\workspace\python\crs_dots\log\crs_dots_load_20190912_212756.sllog
 20190912_212756 loadTraceFlags: game_results,game,adding_list,SkipFile
 20190912_212756 crs_dots_load.py --results_dir=../test_gmres

 20190912_212756 args: Namespace(ncol=None, nrow=None, results_dir='../test_gmres', results_files=True, test_file=None, trace='')

 20190912_212756 Files loaded from directory: ../test_gmres
 20190912_212756     file ../test_gmres\dotsgame_20190912_123600.gmres     ngame=100 nrow=4 ncol=4 gmavg=0.146 sec (min=0.125 max=0.734) sqavg=0.009 sec
 20190912_212756     file ../test_gmres\dotsgame_20190912_124113.gmres     ngame=100 nrow=4 ncol=4 gmavg=1.062 sec (min=0.922 max=1.718) sqavg=0.066 sec
 20190912_212756     file ../test_gmres\dotsgame_20190912_132034.gmres     ngame=100 nrow=8 ncol=8 gmavg=0.934 sec (min=0.867 max=1.296) sqavg=0.015 sec
 20190912_212756 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..	est_gmres --display_game=False --profile_running=True --numgame=100
 20190912_212756     file ../test_gmres\dotsgame_20190912_133855.gmres     ngame=100 nrow=8 ncol=8 gmavg=0.950 sec (min=0.862 max=1.429) sqavg=0.015 sec
 20190912_212756 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..	est_gmres --display_game=True --profile_running=True --numgame=100

 20190912_212756     file ../test_gmres\dotsgame_20190912_142225.gmres     ngame=100 nrow=8 ncol=8 gmavg=4.872 sec (min=3.488 max=8.804) sqavg=0.076 sec
 20190912_212756 
pgm history None
 20190912_212756 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..\test_gmres --display_game=False --profile_running=True --numgame=100

 20190912_212756     file ../test_gmres\dotsgame_20190912_152612.gmres     ngame=100 nrow=8 ncol=8 gmavg=0.955 sec (min=0.863 max=1.388) sqavg=0.015 sec
 20190912_212757 
pgm history beginning
 20190912_212757 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..\test_gmres --display_game=False --profile_running=True --numgame=100

 20190912_212757     file ../test_gmres\dotsgame_20190912_154454.gmres     ngame=100 nrow=8 ncol=8 gmavg=0.959 sec (min=0.862 max=1.582) sqavg=0.015 sec
 20190912_212757 
pgm history beginning
 20190912_212757 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..\test_gmres --display_game=True --profile_running=True --numgame=100

 20190912_212757     file ../test_gmres\dotsgame_20190912_154828.gmres     ngame=100 nrow=8 ncol=8 gmavg=4.345 sec (min=4.099 max=5.318) sqavg=0.068 sec
 20190912_212757 
pgm history shadow_get_legal_moves
 20190912_212757 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..\test_gmres --profile_running=True --numgame=100

 20190912_212757     file ../test_gmres\dotsgame_20190912_211155.gmres     ngame=100 nrow=8 ncol=8 gmavg=3.354 sec (min=3.149 max=3.936) sqavg=0.052 sec
 20190912_212757 
pgm history shadow_get_legal_moves
 20190912_212757 run_info crs_dots.py --nx=8 --ny=8 --run_game=true --loop=true --loop_after=0 --results_dir=..\test_gmres --display_game=False --profile_running=True --numgame=100

 20190912_212757     file ../test_gmres\dotsgame_20190912_211841.gmres     ngame=100 nrow=8 ncol=8 gmavg=0.957 sec (min=0.866 max=1.239) sqavg=0.015 sec
 20190912_212757 End loading 10 files
 20190912_212757 1000 games in 10 files
 20190912_212757  Game Statistics by number of rows, cols
 20190912_212757 rows cols Games
 20190912_212757    4    4   200
 20190912_212757    8    8   800
 20190912_212757  Detailed Game Statistics by number of rows, cols
 20190912_212757 rows cols games  pl   win(%   ) [(%sqs)]  loss(%   ) [(%sqs)]  tie (%   ) [(%sqs)]  
 20190912_212757    4    4   200   1    77(38.5) [(69.0)]   94(47.0) [(31.0)]   29(14.5) [(50.0)]
 20190912_212757    4    4   200   2    94(47.0) [(69.0)]   77(38.5) [(31.0)]   29(14.5) [(50.0)]
 20190912_212757 ----------------------------------------------------------------------
 20190912_212757    8    8   800   1   358(44.8) [(60.1)]  392(49.0) [(39.6)]   50( 6.2) [(50.0)]
 20190912_212757    8    8   800   2   392(49.0) [(60.4)]  358(44.8) [(39.9)]   50( 6.2) [(50.0)]
 20190912_212757 ----------------------------------------------------------------------
 20190912_212757 Saving properties file C:\Users\raysm\workspace\python\crs_dots\crs_dots_load.properties
 20190912_212757 Closing log file C:\Users\raysm\workspace\python\crs_dots\log\crs_dots_load_20190912_212756.sllog

```
