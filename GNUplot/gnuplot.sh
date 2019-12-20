#!/bin/bash
#reset;
#set terminal png;
#set output "robot_radius_basic_pb_1.png";
echo 'reset;
      set terminal png;
      set output "robot_radius_basic_pb_1.png";
      set title noenhanced;
      set xlabel noenhanced;
      f(x) = x**0.25;
      g(x) = x == 0.038 ? 0.03 : 0.09 + (x / 10.0);
      h(x) = 0.04 <= x && x <= 0.1 ? x : g(x);
      set yrange [0:f(200)];
      set ytics ("0" 0, "0.1" f(0.1), "0.25" f(0.25), "0.5" f(0.5),\
        "1" f(1), "2" f(2), "5" f(5), "10" f(10), "20" f(20),"50" f(50), "100" f(100),"200" f(200)) nomirror;
      set xtics ("0.038" h(0.038), "0.04" h(0.04), "0.05" h(0.05), "0.06" h(0.06), "0.07" h(0.07),\
        "0.08" h(0.08), "0.09" h(0.09), "0.1" h(0.1),"0.2" h(0.2), "0.3" h(0.3), "0.5" h(0.5),\
        "0.7" h(0.7), "0.9" h(0.9)) nomirror;
      set key title "Algorithme"; set key box lw 2;
      set grid;
      set title "Temps de résolution des différents algorithmes en fonction de\nrobot_radius pour le fichier basic_problem_1.json";
      set xlabel " robot_radius ";
      set ylabel " temps (en seconde) ";
      set y2label textcolor rgb "purple" "Nombre minimum de défenseurs dans la solution";
      set y2tics textcolor rgb "purple"; set y2range [0:9];
      set style fill transparent solid 0.3;
      plot "datas/basic_pb_1_robot_radius.dat" using (h($1)):(f($2)) title "exact" with linespoints pointtype 7 lc rgb "red",\
      "datas/basic_pb_1_robot_radius.dat" using (h($1)):(f($4)) title "generation" with filledcurve x1 lc rgb "green",\
      "datas/basic_pb_1_robot_radius.dat" using (h($1)):(f($3)) title "glouton" with linespoints pointtype 7 lc rgb "blue",\
      "datas/basic_pb_1_robot_radius.dat" using (h($1)):5 axes x1y2 with points pointtype 13 pointsize 2 lc rgb "purple" notitle; pause 100'|gnuplot
