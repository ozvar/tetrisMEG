import os

start_dir = raw_input("Enter path, such as '../data': ")

outfile_name = raw_input("Enter output filename, such as 'all_episodes.tsv': ")

subject_dirs = os.listdir(start_dir)

subject_dirs = [d for d in subject_dirs if os.path.isdir(os.path.join(start_dir,d))]


epfile_in = None


headers = []
all_lines = []

#Read all the files
for sd in subject_dirs:
    
    print "Session: " + sd
    #subj_files = os.listdir(os.path.join(start_dir,sd))
    
    try:
        epfile_in = open(os.path.join(start_dir, sd, 'episodes_' + sd + '.tsv'), 'r')
        
        
        lines = epfile_in.readlines()
        
        epfile_header = lines[0].strip('\n').split('\t')
        
        #dump each line into a dictionary
        for line in lines[1:]:
            l = {}
            for ix, item in enumerate(line.strip('\n').split('\t')):
                l[epfile_header[ix]] = item
            all_lines.append(l)
        
        headers.append(epfile_header)

        epfile_in.close()
    
    except:
        print "Skipping non-subject folder: " + sd


#Resolve differences in headers

print("Resolving headers.")

out_header = headers[0]
for h in headers[1:]:
    for i in h:
        if i not in out_header:
            out_header.append(i)


print("Writing lines...")

outfile = open(outfile_name, 'w')

outfile.write("\t".join(out_header) + "\n")


for l in all_lines:
    linelist = []
    for k in out_header:
        try:
            item = l[k]
        except KeyError:
            item = "NIL"
        linelist.append(item)

    outfile.write("\t".join(linelist) + "\n")


outfile.close()
    
print("Complete! Closing files.")
        
    
