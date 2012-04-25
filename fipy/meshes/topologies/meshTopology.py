#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "gridTopology.py"
 #
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #  Author: James O'Beirne <james.obeirne@gmail.com>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 # ###################################################################
 ##

__docformat__ = 'restructuredtext'

__all__ = []

from fipy.tools import numerix

from fipy.meshes.topologies.abstractTopology import _AbstractTopology

class _MeshTopology(_AbstractTopology):
    
    @property
    def _concatenatedClass(self):
        from fipy.meshes.mesh import Mesh
        return Mesh

    @property
    def _isOrthogonal(self):
        return False

    @property
    def _cellTopology(self):
        """return a map of the topology of each cell"""
        facesPerCell = self.mesh._facesPerCell
        nodesPerFace = self.mesh._nodesPerFace
        
        def faceCountsMatch(targetCounts):
            if len(targetCounts) > nodesPerFace.shape[0]:
                # pad nodesPerFace with zeros
                paddedNodesPerFace = numerix.zeros((len(targetCounts), nodesPerFace.shape[1]), dtype=int)
                paddedNodesPerFace[:nodesPerFace.shape[0], :] = nodesPerFace
                
                paddedTargetCounts = numerix.array(targetCounts)[..., numerix.newaxis]
            else:
                # pad target face node count with zeros
                paddedTargetCounts = numerix.concatenate((targetCounts,
                                                          [0] * (self.mesh._maxFacesPerCell - len(targetCounts))))
                paddedTargetCounts = paddedTargetCounts[..., numerix.newaxis]
                
                paddedNodesPerFace = nodesPerFace
                
            return ((facesPerCell == len(targetCounts))
                    & (paddedNodesPerFace == paddedTargetCounts).all(axis=0))

        cellTopology = numerix.empty((self.mesh.numberOfCells,), dtype=numerix.ubyte)
        
        t = self._elementTopology
        cellTopology[:] = t["unknown"]
        
        cellTopology[faceCountsMatch([3, 3, 3, 3])] = t["tetrahedron"]
        cellTopology[faceCountsMatch([4, 4, 4, 4, 4, 4])] = t["hexahedron"]
        cellTopology[faceCountsMatch([4, 4, 4, 3, 3])] = t["prism"]
        cellTopology[faceCountsMatch([4, 3, 3, 3, 3])] = t["pyramid"]
        
        return cellTopology

class _Mesh1DTopology(_MeshTopology):
    
    @property
    def _concatenatedClass(self):
        from fipy.meshes.mesh1D import Mesh1D
        return Mesh1D

    @property
    def _isOrthogonal(self):
        return True
        
    @property
    def _cellTopology(self):
        """return a map of the topology of each cell of grid"""
        cellTopology = numerix.empty((self.mesh.numberOfCells,), dtype=numerix.ubyte)
        cellTopology[:] = self._elementTopology["line"]
        
        return cellTopology

class _Mesh2DTopology(_MeshTopology):
    
    @property
    def _concatenatedClass(self):
        from fipy.meshes.mesh2D import Mesh2D
        return Mesh2D
    
    @property
    def _cellTopology(self):
        """return a map of the topology of each cell"""
        cellTopology = numerix.empty((self.mesh.numberOfCells,), dtype=numerix.ubyte)
        
        t = self._elementTopology
        cellTopology[:] = t["polygon"]
        
        facesPerCell = self.mesh._facesPerCell
        cellTopology[facesPerCell == 3] = t["triangle"]
        cellTopology[facesPerCell == 4] = t["quadrangle"]
        
        return cellTopology
        
