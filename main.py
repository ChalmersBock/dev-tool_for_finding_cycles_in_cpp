import networkx as nx
from pathlib import Path
import pydot
import os

STD_LIBS = {
    "algorithm",
    "future",
    "numeric",
    "strstream",
    "any",
    "initializer_list",
    "optional",
    "system_error",
    "array",
    "iomanip",
    "ostream",
    "thread",
    "atomic",
    "ios",
    "queue",
    "tuple",
    "bitset",
    "iosfwd",
    "random",
    "type_traits",
    "chrono",
    "iostream",
    "ratio",
    "typeindex",
    "codecvt",
    "istream",
    "regex",
    "typeinfo",
    "complex",
    "iterator",
    "scoped_allocator",
    "unordered_map",
    "condition_variable",
    "limits",
    "set",
    "unordered_set",
    "deque",
    "list",
    "shared_mutex",
    "utility",
    "exception",
    "locale",
    "sstream",
    "valarray",
    "execution",
    "map",
    "stack",
    "variant",
    "filesystem",
    "memory",
    "stdexcept",
    "vector",
    "forward_list",
    "memory_resource",
    "streambuf",
    "fstream",
    "mutex",
    "string",
    "functional",
    "new",
    "string_view",
    "cassert",
    "cinttypes",
    "csignal",
    "cstdio",
    "cwchar",
    "ccomplex",
    "ciso646",
    "cstdalign",
    "cstdlib",
    "cwctype",
    "cctype",
    "climits",
    "cstdarg",
    "cstring",
    "cerrno",
    "clocale",
    "cstdbool",
    "ctgmath",
    "cfenv",
    "cmath",
    "cstddef",
    "ctime",
    "cfloat",
    "csetjmp",
    "cstdint",
    "cuchar",
    "concepts",
    "coroutine",
    "compare",
    "version",
    "source_location",
    "format",
    "span",
    "ranges",
    "bit",
    "numbers",
    "syncstream",
    "stop_token",
    "semaphore",
    "latch",
    "barrier"
}


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


def is_standard_library(file_name):
    return file_name in STD_LIBS


def outgoing_dependencies(file_path):
    # Return a list of file names that the current 'file_path' includes with
    # the #include-statement
    dependencies = []
    with open(file_path, encoding='utf-8') as f:
        for line in f.readlines():
            if is_include_statement(line):
                included_file = line.split()[-1].strip("\"<>").rsplit("/", 1)[-1]
                if not is_standard_library(included_file):
                    dependencies.append(included_file)

    return dependencies


def edges(start_node, out_nodes):
    # Returns a list of tuples, representing each edge from 'start_node'
    # to each other node in the 'out_nodes' list
    return [(start_node, out_node) for out_node in out_nodes]


def filename_from_full_path(full_path):
    # Extract filename from full path
    return str(full_path).rsplit("\\", 1)[-1]

def color_cycle(g, cycle):
    g.get_edge(cycle[-1], cycle[0])[0].set_color("red")
    g.get_node(cycle[-1])[0].set_fillcolor("pink")
    g.get_node(cycle[-1])[0].set_style("filled")
    for i in range(len(cycle) - 1):
        g.get_edge(cycle[i], cycle[i + 1])[0].set_color("red")
        g.get_node(cycle[i])[0].set_fillcolor("pink")
        g.get_node(cycle[i])[0].set_style("filled")

def write_cycle(cycle, index):
    cycle_graph = pydot.Dot("Cycle_graph", graph_type="digraph")
    for n in cycle:
        cycle_graph.add_node(pydot.Node(n))

    cycle_graph.add_edge(pydot.Edge(cycle[-1], cycle[0]))
    for i in range(len(cycle) - 1):
        cycle_graph.add_edge(pydot.Edge(cycle[i], cycle[i+1]))

    cycle_graph.write_png(f'dependency_graphs/png/cycle_{index}.png')
    cycle_graph.write_svg(f'dependency_graphs/svg/cycle_{index}.svg')

def create_directory(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        print(f'{path}: Directory already exists')

def draw_cycle_graph(g, g_cycles):
    # Draw a visual representation of the nodes and edges
    # that are present in the detected cycles

    create_directory("dependency_graphs")
    create_directory("dependency_graphs/svg")
    create_directory("dependency_graphs/png")

    counter = 0
    for cycle in g_cycles:
        color_cycle(g, cycle)
        write_cycle(cycle, counter)
        counter += 1

    g.write_png("dependency_graphs/png/graph.png")
    g.write_svg("dependency_graphs/svg/graph.svg")


# WARNING, Does not function correctly if you have to files with exactly the same name in different folders
# e.g. src/main.cpp and test/main.cpp
if __name__ == '__main__':

    print("\nAnalyzing directory ...\n")

    FILE_TYPES = ('*.c', '*.cpp', '*.h', '*.hpp')
    EXCLUDE_DIRS = ('build', 'test')

    graph = pydot.Dot("Dependency graph", graph_type="digraph")

    c_and_h_paths = relevant_file_paths(os.getcwd(), FILE_TYPES, EXCLUDE_DIRS)
    shortened_paths = [filename_from_full_path(p) for p in c_and_h_paths]

    for node in shortened_paths:
        # Dots must be replaced with underscores, causes issues
        graph.add_node(pydot.Node(node.replace(".", "_"), label=node))

    for node in c_and_h_paths:
        for dep in outgoing_dependencies(node):  # We need to make sure that all nodes are correctly labeled
            name = filename_from_full_path(dep)
            if len(graph.get_node(name.replace(".", "_"))) == 0:
                graph.add_node(pydot.Node(name.replace(".", "_"), label=name))

        for src, dest in edges(filename_from_full_path(node), outgoing_dependencies(node)):
            # Dots must be replaced with underscores, causes issues
            graph.add_edge(pydot.Edge(src.replace(".", "_"), dest.replace(".", "_")))

    print(f"Found {len(graph.get_nodes())} relevant files with {len(graph.get_edges())} total dependencies")

    nx_graph = nx.drawing.nx_pydot.from_pydot(graph)
    cycles = list(nx.simple_cycles(nx_graph))
    output = "No circular dependencies were found"
    if cycles:
        output = f"{len(cycles)} cycle(s) were found: {cycles}"
    print(f"{output}\n")

    draw_cycle_graph(graph, cycles)
