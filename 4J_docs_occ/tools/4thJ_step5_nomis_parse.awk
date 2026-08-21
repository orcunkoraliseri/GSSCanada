{
  line=$0; n=0; f=""; inq=0; delete a
  for (i=1;i<=length(line);i++){
    c=substr(line,i,1)
    if (c=="\"") { inq=!inq; continue }
    if (c=="," && !inq) { a[++n]=f; f=""; continue }
    f=f c
  }
  a[++n]=f
  printf "%s\t%s\t%s\n", a[14], a[15], a[21]
}
