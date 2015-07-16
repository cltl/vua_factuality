###########################################################
### renumber.features.file.pl
### Roser Morante, July 2015
### Incorporates the predictions of a machine learner into teh foreval files where cues are listed with their tokens
### Input format: files in feature_files directory
### wsj_0745.tml	10	t181	180	an	a	D	DT	t183	NMOD	O	hold-15.1	NULL
### usage: renumber.features.file.pl [-h -v] -d <directory where the feature files are>  

###########################################################
#!/usr/bin/perl
#use strict;
use warnings; 
use Getopt::Std;

my $directory = '';
my $file = "";
my $fileOut = "";

#############################################################
###### parameters
#############################################################

our ($opt_h, $opt_d, $opt_v);

getopts("d:o:hv") ;


if ((defined $opt_h) || (!(defined $opt_d) )){

print<<'EOT';
      Scripts that renumbers tokens and dependencies

      renumber.features.file.pl [-h -v] -d <directory where the feature files are>  
      
      Optional parameter:

      -h : help

      -v : verbose. Prints processing information
EOT
  exit;
}



$directory = $opt_d;


my $line;
my $countwords = 0;
my $file_prefix = "";



my @columns = ();
my @sentence = ();


my @col_file = ();
my @col_sentence_id = ();
my @col_term_id = ();
my @col_token_id = ();
my @col_word = ();
my @col_lemma = ();
my @col_pos = ();
my @col_morphofeat = ();
my @col_dep = ();
my @col_deplabel = ();
my @col_event_bio = ();
my @col_pb = ();
my @col_vn = ();
my @col_fn = ();
my @col_wn = ();
my @col_eventtype = ();
my @col_eso = ();
my @col_nombank = ();
my @col_role_bio = ();
my @col_token_id_sent = ();

my %terms_index = ();

my $sentence_number = 0;

######################
###### MAIN 
######################

opendir (DIR, $directory) or die $!;


while ($file = readdir(DIR)) {
  
  if (defined $opt_v) {
    print "processing directory $directory\n";
    print "processing file $file\n";
  }


  ## checking that $file is a file and not a directory
  next unless (-f "$directory/$file");
  ## checking that file has .features extension
  next unless ("$directory/$file" =~ /^.+features.tsv$/);
  
 
  
  open(OUTFILE, ">$directory/$file.renumbered")  || die "Cannot open output file\n"; 
  open(FILE, "$directory/$file") || die "Cannot open file with features\n";

  
  read_features_file();
  
  
  close(FILE);
  close(OUTFILE);   
  
  
} #closes while  that reads directory

closedir(DIR);

##################################
sub read_features_file {

@columns = ();
@sentence = ();

@col_file = ();
@col_sentence_id = ();
@col_term_id = ();
@col_token_id = ();
@col_word = ();
@col_lemma = ();
@col_pos = ();
@col_morphofeat = ();
@col_dep = ();
@col_deplabel = ();
@col_event_bio = ();
@col_pb = ();
@col_vn = ();
@col_fn = ();
@col_wn = ();
@col_eventtype = ();
@col_eso = ();
@col_nombank = ();
@col_role_bio = ();

@col_token_id_sent = ();

%terms_token_number = ();

$sentence_number = 0; 
$countwords = 0;

  while(<FILE>){
    $line = $_;
    chomp $line;

    @columns = ();
    @columns = split /\t/, $line;
    #first line in doc
    if (eof FILE){
      $countwords++;
      $sentence_number = $columns[1];
      push @col_file, $columns[0];
      push @col_sentence_id, $columns[1];
      push @col_term_id, $columns[2];
      push @col_token_id, $columns[3];
      push @col_word, $columns[4];
      push @col_lemma, $columns[5];
      push @col_pos, $columns[6];
      push @col_morphofeat, $columns[7];
      push @col_dep, $columns[8];
      push @col_deplabel, $columns[9];
      push @col_event_bio, $columns[10];
      push @col_pb, $columns[11];
      push @col_vn, $columns[12];
      push @col_fn, $columns[13];
      push @col_wn, $columns[14];
      push @col_eventtype, $columns[15];
      push @col_eso, $columns[16];
      push @col_nombank, $columns[17];
      push @col_role_bio, $columns[18];
      $term_token_number{"$columns[2]"} = "$countwords";
      process_sentence();
    } elsif ($sentence_number == 0){
      $countwords++;
      $sentence_number = $columns[1];
      push @col_file, $columns[0];
      push @col_sentence_id, $columns[1];
      push @col_term_id, $columns[2];
      push @col_token_id, $columns[3];
      push @col_word, $columns[4];
      push @col_lemma, $columns[5];
      push @col_pos, $columns[6];
      push @col_morphofeat, $columns[7];
      push @col_dep, $columns[8];
      push @col_deplabel, $columns[9];
      push @col_event_bio, $columns[10];
      push @col_pb, $columns[11];
      push @col_vn, $columns[12];
      push @col_fn, $columns[13];
      push @col_wn, $columns[14];
      push @col_eventtype, $columns[15];
      push @col_eso, $columns[16];
      push @col_nombank, $columns[17];
      push @col_role_bio, $columns[18];
      $term_token_number{"$columns[2]"} = "$countwords";
      # lines with same sentence number
    } elsif ($sentence_number > 0 && $columns[1] == $sentence_number){
      $countwords++;
      $sentence_number = $columns[1];
      push @col_file, $columns[0];
      push @col_sentence_id, $columns[1];
      push @col_term_id, $columns[2];
      push @col_token_id, $columns[3];
      push @col_word, $columns[4];
      push @col_lemma, $columns[5];
      push @col_pos, $columns[6];
      push @col_morphofeat, $columns[7];
      push @col_dep, $columns[8];
      push @col_deplabel, $columns[9];
      push @col_event_bio, $columns[10];
      push @col_pb, $columns[11];
      push @col_vn, $columns[12];
      push @col_fn, $columns[13];
      push @col_wn, $columns[14];
      push @col_eventtype, $columns[15];
      push @col_eso, $columns[16];
      push @col_nombank, $columns[17];
      push @col_role_bio, $columns[18];
      $term_token_number{"$columns[2]"} = "$countwords";
      # line with a difference sentence number than previous
    } elsif ($sentence_number > 0 && $columns[1] != $sentence_number){

      process_sentence();
     print OUTFILE "\n";
      $countwords = 0;
      @col_file = ();
      @col_sentence_id = ();
      @col_term_id = ();
      @col_token_id = ();
      @col_word = ();
      @col_lemma = ();
      @col_pos = ();
      @col_morphofeat = ();
      @col_dep = ();
      @col_deplabel = ();
      @col_event_bio = ();
      @col_pb = ();
      @col_vn = ();
      @col_fn = ();
      @col_wn = ();
      @col_eventtype = ();
      @col_eso = ();
      @col_nombank = ();
      @col_role_bio = ();
      @col_token_id_sent = ();
     %terms_token_number = ();
     $sentence_number = $columns[1];
     $countwords++;
      push @col_file, $columns[0];
      push @col_sentence_id, $columns[1];
      push @col_term_id, $columns[2];
      push @col_token_id, $columns[3];
      push @col_word, $columns[4];
      push @col_lemma, $columns[5];
      push @col_pos, $columns[6];
      push @col_morphofeat, $columns[7];
      push @col_dep, $columns[8];
      push @col_deplabel, $columns[9];
      push @col_event_bio, $columns[10];
      push @col_pb, $columns[11];
      push @col_vn, $columns[12];
      push @col_fn, $columns[13];
      push @col_wn, $columns[14];
      push @col_eventtype, $columns[15];
      push @col_eso, $columns[16];
      push @col_nombank, $columns[17];
      push @col_role_bio, $columns[18];
      $term_token_number{"$columns[2]"} = "$countwords";

   } 
   

   }##closes while over FILE

}#closes sub read features file

###############################################
sub process_sentence {


my $token_id_sent = 0;
my $index = 0;


for ($i=0;$i<$countwords;$i++){
  $token_id_sent = $i + 1;
  push @col_token_id_sent, "$token_id_sent";
}


for ($i=0;$i<$countwords;$i++){
  print OUTFILE "$col_file[$i]\t";
  print OUTFILE "$col_sentence_id[$i]\t";
  print OUTFILE "$col_term_id[$i]\t";
  print OUTFILE "$col_token_id_sent[$i]\t";
  print OUTFILE "$col_word[$i]\t";
  print OUTFILE "$col_lemma[$i]\t";
  print OUTFILE "$col_pos[$i]\t";
  print OUTFILE "$col_morphofeat[$i]\t";
  if ($col_dep[$i] eq "NULL"){
    print OUTFILE  "0\t";
  } else{
    print OUTFILE "$term_token_number{$col_dep[$i]}\t";
  }
  print OUTFILE "$col_deplabel[$i]\t";
  print OUTFILE "$col_event_bio[$i]\t";
  print OUTFILE "$col_pb[$i]\t";
  print OUTFILE "$col_vn[$i]\t";
  print OUTFILE "$col_fn[$i]\t";
  print OUTFILE "$col_wn[$i]\t";
  print OUTFILE "$col_eventtype[$i]\t";
  print OUTFILE "$col_eso[$i]\t";
  print OUTFILE "$col_nombank[$i]\t";
  print OUTFILE "$col_role_bio[$i]";
  print OUTFILE "\n";
}



}#closes sub process_sentence
