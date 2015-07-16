###########################################################
### generate.instances.factuality.pl
### Roser Morante, April 2015
### Generates instances for the factuality classification task
### Input format: tab separated columns
###               
### Output format: tab separated columns
###
###
### usage: generate.instances.cues.pl [-h -v] -d <directory where files are> -o <output directory> 
###########################################################

#!/usr/bin/perl
#use strict;
use warnings; 
use Getopt::Std;

my $directory = '';
my $subdirectory = "";
my $file = "";
my $fileOut = "";

#############################################################
###### parameters
#############################################################

our ($opt_h, $opt_d, $opt_v, $opt_o) ;

getopts("d:o:hv") ;


if ( (defined $opt_h) || ( (!(defined $opt_d)) || (!(defined $opt_o)) )){

print<<'EOT';
      Scripts that generates instances from 

      [perl] generate.instances.cues.pl [OPTIONS] -d <directory where the feature files with class are> -o <directory where the output has to be written>
      
      Optional parameter:

      -h : help

      -v : verbose. Prints processing information
EOT
  exit;
}



$directory = $opt_d;
$out_directory = $opt_o;


my $line;
my $countwords = 0;


my @columns = ();
my @sentence = ();

my @col_file = ();
my @col_sentence = ();
my @col_token_doc = ();
my @col_token_sent = ();
my @col_word = ();
my @col_lemma = ();
my @col_pos = ();
my @col_morpho = ();
my @col_dep = ();
my @col_deplabel = ();
my @col_event = ();
my @col_pb = ();
my @col_vn = ();
my @col_fn = ();
my @col_wn = ();
my @col_nb = ();
my @class = ();

my $excluded_verbs = '(do|did|does|do|have|has|had|was|were|is|are|been|is|\'s|\'m|\'re|\'ve)';


######################
###### MAIN 
######################

opendir (DIR, $directory) or die $!;


 while (my $file = readdir(DIR)) {

   if (defined $opt_v) {
     print "processing directory $directory\n";
     print "processing file $file\n";
   }
   
   ## checking that $file is a file and not a directory
   next unless (-f "$directory/$file");
   ## checking that file has .features extension
   next unless ("$file" =~ /^.+renumbered$/);
   
   open (OUTFILE, ">$out_directory\/$file.inst")  || die "Cannot open output instances file $out_directory\/$file.inst\n"; 
   open(FILE, "$directory/$file") || die "Cannot open features file $directory/$file\n";

   while(<FILE>){
     $line = $_;
     chomp $line;
     #print OUTFILE  "line= $line\n";
     ##processing empty lines
     if ($line eq ""){
      # print OUTFILE  "$line is empty\n";
       $countwords = $#col_word;
       process_sentence();
       $countwords = 0;
       @col_file = ();
       @col_sentence = ();
       @col_token_doc = ();
       @col_token_sent = ();
       @col_word = ();
       @col_lemma = ();
       @col_pos = ();
       @col_morpho = ();
       @col_dep = ();
       @col_deplabel = ();
       @col_event = ();
       @col_pb = ();
       @col_vn = ();
       @col_fn = ();
       @col_wn = ();
       @col_nb = ();
       @class = ();
     #### processing last line of file
     } elsif (eof){      
       @columns = split /\t/, $line;
       push @col_file, $columns[0];
       push @col_sentence, $columns[1];
       push @col_token_doc, $columns[2];
       push @col_token_sent, $columns[3];
       push @col_word, $columns[4];
       push @col_lemma, $columns[5];
       push @col_pos, $columns[6];
       push @col_morpho, $columns[7];
       push @col_dep, $columns[8];
       push @col_deplabel, $columns[9];
       push @col_event, $columns[10];
       push @col_pb, $columns[11];
       push @col_vn, $columns[12];
       push @col_fn, $columns[13];
       push @col_wn, $columns[14];
       push @col_nb, $columns[74];
       push @class, $columns[19];
       $countwords = $#col_word;
       process_sentence();
       $countwords = 0;
       @col_file = ();
       @col_sentence = ();
       @col_token_doc = ();
       @col_token_sent = ();
       @col_word = ();
       @col_lemma = ();
       @col_pos = ();
       @col_morpho = ();
       @col_dep = ();
       @col_deplabel = ();
       @col_event = ();
       @col_pb = ();
       @col_vn = ();
       @col_fn = ();
       @col_wn = ();
       @col_nb = ();
       @class = ();

       ###processing lines that are not empty and are not last line of file
     } elsif ($line =~ /^.+\t.+\t.+$/) { 
       #print OUTFILE "I am in else\n";
       #print OUTFILE "line in else is $line\n";
        @columns = split /\t/, $line;
       push @col_file, $columns[0];
       push @col_sentence, $columns[1];
       push @col_token_doc, $columns[2];
       push @col_token_sent, $columns[3];
       push @col_word, $columns[4];
       push @col_lemma, $columns[5];
       push @col_pos, $columns[6];
       push @col_morpho, $columns[7];
       push @col_dep, $columns[8];
       push @col_deplabel, $columns[9];
       push @col_event, $columns[10];
       push @col_pb, $columns[11];
       push @col_vn, $columns[12];
       push @col_fn, $columns[13];
       push @col_wn, $columns[14];
       push @col_nb, $columns[74];
       push @class, $columns[19];

     } 

   } ### closes while that reads lines in file
  


   close(FILE);
   close(OUTFILE);
   
 } #closes while  that reads directory



###################### subroutine process_sentence #############################



sub process_sentence {




  #print OUTFILE "I am in process sentence\n";

  ########## printing features #################



  for ($i=0;$i<=$countwords;$i++){

    
    ## we only print V
    if ($col_event[$i] eq "BEvent"){
      ##############################
      #### data focus token ########
      #############################

      #### identifiers ################
      print OUTFILE "$col_file[$i]\t";
      print OUTFILE "$col_sentence[$i]\t";
      print OUTFILE "$col_token_doc[$i]\t";
      print OUTFILE "$col_token_sent[$i]\t"; 
    
       #### lemma, word, pos, deplabel ####
      print OUTFILE "$col_lemma[$i]\t";
      print OUTFILE "$col_word[$i]\t";
      print OUTFILE "$col_pos[$i]\t";
      print OUTFILE "$col_morpho[$i]\t";
      print OUTFILE "$col_deplabel[$i]\t";

      ### lexical info
      print OUTFILE "$col_pb[$i]\t";
      print OUTFILE "$col_fn[$i]\t";
      print OUTFILE "$col_wn[$i]\t";
      print OUTFILE "$col_vn[$i]\t";


 
 
      ############## context focus token #####################
      ########### +3 and -3 postype on focus token ###########
      #######################################################
      if (($i-3) >= 0) {
	print OUTFILE "$col_word[$i-3]\t";
	print OUTFILE "$col_lemma[$i-3]\t";
	print OUTFILE "$col_pos[$i-3]\t";
	print OUTFILE "$col_morpho[$i-3]\t";
	print OUTFILE "$col_deplabel[$i-3]\t";
      } else {
	print OUTFILE "_\t_\t_\t_\t_\t";
      }
      if (($i-2) >= 0) {
	print OUTFILE "$col_word[$i-2]\t";
	print OUTFILE "$col_lemma[$i-2]\t";
	print OUTFILE "$col_pos[$i-2]\t";
	print OUTFILE "$col_morpho[$i-2]\t";
	print OUTFILE "$col_deplabel[$i-2]\t";
      } else {
	print OUTFILE "_\t_\t_\t_\t_\t";
      }
      if (($i-1) >= 0) {
	print OUTFILE "$col_word[$i-1]\t";
	print OUTFILE "$col_lemma[$i-1]\t";
	print OUTFILE "$col_pos[$i-1]\t";
	print OUTFILE "$col_morpho[$i-1]\t";
	print OUTFILE "$col_deplabel[$i-1]\t";
      } else {
	print OUTFILE "_\t_\t_\t_\t_\t";
      }
      if (($i+1) <= $countwords){
	print OUTFILE "$col_word[$i+1]\t";
	print OUTFILE "$col_lemma[$i+1]\t";
	print OUTFILE "$col_pos[$i+1]\t";
	print OUTFILE "$col_morpho[$i+1]\t";
	print OUTFILE "$col_deplabel[$i+1]\t";
      } else {
	print OUTFILE "_\t_\t_\t_\t_\t";
      }
      if (($i+2) <= $countwords){
	print OUTFILE "$col_word[$i+2]\t";
	print OUTFILE "$col_lemma[$i+2]\t";
	print OUTFILE "$col_pos[$i+2]\t";
	print OUTFILE "$col_morpho[$i+2]\t";
	print OUTFILE "$col_deplabel[$i+2]\t";
      } else {
	print OUTFILE "_\t_\t_\t_\t_\t";
      }
      if (($i+3) <= $countwords){
	print OUTFILE "$col_word[$i+3]\t";
	print OUTFILE "$col_lemma[$i+3]\t";
	print OUTFILE "$col_pos[$i+3]\t";
	print OUTFILE "$col_morpho[$i+2]\t";
	print OUTFILE "$col_deplabel[$i+3]\t";
      } else {
	print OUTFILE "_\t_\t_\t_\t_\t";
      }


      #######################################
      #####  look for children of token
      #######################################
      
      ## contains indexes children of token
      my @indexes_children = ();
      
      for ($z=0;$z<=$countwords;$z++){
	next unless ($col_dep[$z] ne "_");
	if ($col_dep[$z] == $col_token_sent[$i]){
	  push @indexes_children, $z;
	}
      }
      
      ###########################################
      ##### features children of token ##########
      ###########################################
      
      my $POSChildren = "";
      my $chunkChildren  = "";
      my $depLabelChildren  = "";
      
      if (@indexes_children){ #####here
	
	my $count_children = $#indexes_children;
	
	for ($x=0;$x<=$count_children;$x++){
	  
	  if ($POSChildren  eq ""){
	    $POSChildren  = "$col_pos[$indexes_children[$x]]";
	  } else {
	    $POSChildren  = "$POSChildren" . "_" . "$col_pos[$indexes_children[$x]]";
	  }
	  
	  
	  if ($depLabelChildren eq ""){
	    $depLabelChildren = "$col_deplabel[$indexes_children[$x]]";
	  } else {
	    $depLabelChildren = "$depLabelChildren" . "_" . "$col_deplabel[$indexes_children[$x]]";
	  }
	  
	}
	
      } else {
	
	$POSChildren = "_";
	$depLabelChildren = "_";
	
      }
      
      print OUTFILE "$POSChildren\t";
      print OUTFILE "$depLabelChildren\t";
  

      ##########################################
      ##### features  father of token  ##########
      ##########################################
    
    ## punctuation signs do not have dependency information
    if ($col_dep[$i] ne "_"){
      $index_father = $col_dep[$i] - 1;
      
      
      if ($col_deplabel[$i] ne "ROOT"){
	
	
	print OUTFILE "$col_lemma[$index_father]\t";
	print OUTFILE "$col_pos[$index_father]\t";
	print OUTFILE "$col_morpho[$index_father]\t";
	print OUTFILE "$col_dep[$index_father]\t";
	print OUTFILE "$col_deplabel[$index_father]\t";
      } else {
	
	print  OUTFILE "_\t_\t_\t_\t_\t";
      }
    } else {
	print  OUTFILE "_\t_\t_\t_\t_\t";
    }
    
    

      ############################################
      ########### class ##########################


 #	print OUTFILE "$class[$i]\n";
      print OUTFILE "_\n";
    } #if pos is verb
  }#loop over tokens
  
} #### end subroutine process sentence

