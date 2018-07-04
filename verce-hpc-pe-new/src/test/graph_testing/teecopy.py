'''
This is a dispy graph which produces a workflow that copies the data (from node prod) to two nodes (cons1 and cons2). 
If you compare this graph with :py:mod:`~test.graph_testing.grouping_onetoall` they look quite similar. 
However, they do different things. 
In this example, the nodes ``cons1`` and ``cons2`` are different PE and the node ``prod`` sends the same data to both PEs.

.. image:: /api/images/teecopy.png

It can be executed with MPI and STORM.

* MPI: Please, locate yourself into the dispy directory. 

    Execute the MPI mapping as follows::

        mpiexec -n <number mpi_processes> python -m dispel4py.worker_mpi <name_dispy_graph> <-f file containing the input dataset in JSON format>
	<-i number of iterations/runs'> <-s>
	
    The argument '-s' forces to run the graph in a simple processing, which means that the first node of the graph will be executed in a process, and the rest of nodes will be        executed in a second process.  
    When <-i number of interations/runs> is not indicated, the graph is executed once by default. 	
    

    For example::
    
        mpiexec -n 3 python -m dispel4py.worker_mpi test.graph_testing.teecopy 
        
    .. note::
    
        Each node in the graph is executed as a separate MPI process. 
        This graph has 3 nodes. For this reason we need at least 3 MPI processes to execute it. 
        
    Output::

        Processing 1 iterations
        Processes: {'TestProducer0': [0], 'TestOneInOneOut2': [2], 'TestOneInOneOut1': [1]}
        TestProducer0 (rank 0): I'm a spout
        Rank 0: Sending terminate message to [1]
        Rank 0: Sending terminate message to [2]
        TestProducer0 (rank 0): Processed 1 input block(s)
        TestProducer0 (rank 0): Completed.
        TestOneInOneOut2 (rank 2): I'm a bolt
        TestOneInOneOut2 (rank 2): Processed 1 input block(s)
        TestOneInOneOut2 (rank 2): Completed.
        TestOneInOneOut1 (rank 1): I'm a bolt
        TestOneInOneOut1 (rank 1): Processed 1 input block(s)
        TestOneInOneOut1 (rank 1): Completed
				
* STORM:  
'''

from test.graph_testing import testing_PEs as t
from dispel4py.workflow_graph import WorkflowGraph

def testTee():
    '''
    Creates a graph with two consumer nodes and a tee connection.
    
    :rtype: the created graph
    '''
    graph = WorkflowGraph()
    prod = t.TestProducer()
    prev = prod
    cons1 = t.TestOneInOneOut()
    cons2 = t.TestOneInOneOut()
    graph.connect(prod, 'output', cons1, 'input')
    graph.connect(prod, 'output', cons2, 'input')
    return graph

''' important: this is the graph_variable '''
graph = testTee()
