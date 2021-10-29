import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import os


def relevant_file_paths(dir_path, relevant_file_types, dirs_to_exclude=None):
    if dirs_to_exclude is None:
        dirs_to_exclude = []

    relevant_files = []
    for file_type in relevant_file_types:
        relevant_files.extend(Path(dir_path).rglob(file_type))

    def dir_name_not_in_path(path):
        return all(ex_dir not in str(path) for ex_dir in dirs_to_exclude)

    # Exclude paths containing directory names from 'dirs_to_exclude' list
    return list(filter(dir_name_not_in_path, relevant_files))


def is_include_statement(line):
    return line.strip().startswith("#include")


def outgoing_dependencies(file_path):
    # Return a list of file names that the current 'file_path' includes with
    # the #include-statement
    dependencies = []
    with open(file_path, encoding='utf-8') as f:
        for line in f.readlines():
            if is_include_statement(line):
                included_file = line.split()[-1].strip("\"<>").rsplit("/", 1)[-1]
                dependencies.append(included_file)
    return dependencies


def edges(start_node, out_nodes):
    # Returns a list of tuples, representing each edge from 'start_node'
    # to each other node in the 'out_nodes' list
    return [(start_node, out_node) for out_node in out_nodes]


def filename_from_full_path(full_path):
    # Extract filename from full path
    return str(full_path).rsplit("\\", 1)[-1]


def draw_cycle_graph(g, g_cycles):
    # Draw a visual representation of the nodes and edges
    # that are present in the detected cycles
    unique_nodes_in_cycle = set([n for cycle in g_cycles for n in cycle])
    nx.draw(g.subgraph(unique_nodes_in_cycle), with_labels=True, font_size=8)
    plt.show()


# WARNING, Does not function correctly if you have to files with exactly the same name in different folders
# e.g. src/main.cpp and test/main.cpp
if __name__ == '__main__':

    print("Analyzing directory ...")

    FILE_TYPES = ('*.c', '*.cpp', '*.h', '*.hpp')
    EXCLUDE_DIRS = ('build', 'test')

    graph = nx.DiGraph()

    c_and_h_paths = relevant_file_paths(os.getcwd(), FILE_TYPES, EXCLUDE_DIRS)
    shortened_paths = [filename_from_full_path(p) for p in c_and_h_paths]
    graph.add_nodes_from(shortened_paths)

    for node in c_and_h_paths:
        graph.add_edges_from(edges(filename_from_full_path(node), outgoing_dependencies(node)))

    print(f"Found {len(graph.nodes)} relevant files with {len(graph.edges)} total dependencies")

    cycles = list(nx.simple_cycles(graph))
    output = "No circular dependencies were found"
    if cycles:
        output = f"{len(cycles)} cycle(s) were found: {cycles}"
    print(output)

    draw_cycle_graph(graph, cycles)
