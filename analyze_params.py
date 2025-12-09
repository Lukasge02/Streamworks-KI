import os
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

def analyze_xmls(start_dir):
    unique_tags = Counter()
    tag_paths = set()
    parent_child_map = defaultdict(set)
    
    # We only care about "Streams" usually, but let's look at what we find.
    # The user mentioned "Streams" in Export-Streams.
    
    for root_dir, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".xml"):
                path = os.path.join(root_dir, file)
                try:
                    tree = ET.parse(path)
                    root = tree.getroot()
                    
                    # We are mostly interested in <Stream> and its children usually
                    # But let's just grab everything to see what's "all parameters"
                    
                    for elem in root.iter():
                        tag = elem.tag
                        unique_tags[tag] += 1
                        
                        # Build a "path" to see structure e.g. Stream/Jobs/Job/JobName
                        # This is a bit expensive for full tree, but let's do a simple parent map
                        # ET doesn't give parent easily during iter, wait.
                        pass

                except Exception as e:
                    # Ignore malformed or non-xml files (some might be parts)
                    pass

    # Re-read to build structure (easier than recursive usually)
    structure = defaultdict(set)
    
    def traverse(node, path=""):
        tag = node.tag
        current_path = f"{path}/{tag}" if path else tag
        structure[current_path] = structure[current_path] # ensure key exists
        
        for child in node:
            structure[current_path].add(child.tag)
            traverse(child, current_path)

    count = 0
    for root_dir, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".xml"):
                try:
                    tree = ET.parse(os.path.join(root_dir, file))
                    root = tree.getroot()
                    traverse(root)
                    count += 1
                    if count > 50: break # Analyze first 50 valid XMLs to get a good sample
                except:
                    pass
        if count > 50: break
    
    print(f"Analyzed {count} files.")
    print("\nStructure found (Parent -> Children):")
    for parent, children in sorted(structure.items()):
        if "Stream" in parent: # Focus on Stream relevant tags
            child_list = ", ".join(sorted(list(children)))
            if child_list:
                print(f"{parent}: [{child_list}]")

if __name__ == "__main__":
    analyze_xmls("Export-Streams")
