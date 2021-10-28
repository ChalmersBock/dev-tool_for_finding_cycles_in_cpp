import networkx as nx
import os


def parse_directory(dir_name):
    # Create a list of file and sub directories
    # Names in the given directory
    list_of_file = os.listdir(dir_name)
    all_relevant_files = list()
    # Iterate over all the entries
    for entry in list_of_file:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        # We are not interested in the build or test directories
        if os.path.isdir(full_path) and not entry.endswith("build") and not entry.endswith("test"):
            all_relevant_files = all_relevant_files + parse_directory(full_path)
        elif entry.endswith(".c") or entry.endswith(".cpp") or entry.endswith(".h") or entry.endswith(".hpp"):
            all_relevant_files.append(full_path)

    return all_relevant_files


def map_includes(all_paths):
    n_map = dict()  # dict that maps names (paths) of files to the names (paths) of files they include
    quick_name = dict()  # dict used for quick loop-up if we already know the full path

    # Iterate over all files to find out what files they include
    for p in all_paths:
        with open(p) as f:
            lines = f.readlines()
            include_list = []  # Used to remember what files are included in a specific file
            for line in lines:
                line.strip(" ")

                if line.startswith("#include") and "<" not in line:
                    _, n, _ = line.split("\"")  # Get the name of the included file (n)
                    n = n.replace("/", "\\")  # Format the name of the file to fit with the path

                    if n in quick_name.keys():  # If we have seen the file name before, we can set the path directly
                        n_full = quick_name[n]
                    else:
                        for p_item in all_paths:  # If we have not seen the file name before, we need to find the path
                            if p_item.endswith(n):
                                quick_name[n] = p_item
                                n_full = p_item

                    include_list.append(n_full)

            n_map[p] = include_list

    return n_map


# WARNING, Does not function correctly if you have to files with exactly the same name in different folders
# e.g. src/main.cpp and test/main.cpp
if __name__ == '__main__':

    path = os.getcwd()
    graph = nx.DiGraph()

    c_and_h_paths = parse_directory(path)

    name_map = map_includes(c_and_h_paths)

    graph.add_nodes_from(name_map.keys())

    for key in name_map:
        for value in name_map[key]:
            graph.add_edge(key, value)

    cycles = nx.simple_cycles(graph)

    for cycle in cycles:
        print(cycle)
