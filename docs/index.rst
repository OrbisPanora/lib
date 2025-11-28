OrbisPanora Parser Documentation
=================================

Welcome to OrbisPanora Parser's documentation. This is an updated version of the anvil-parser2, 
a parser for the Minecraft anvil file format that supports all Minecraft versions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/anvil
   modules/patterns

Installation
------------

You can install the library using pip:

.. code-block:: bash

   pip install git+ssh://git@codefirst.iut.uca.fr/IUT_INF63/projets-etudiants/OrbisPanora/lib.git@origin/dev

Quick Start
-----------

Basic Usage
^^^^^^^^^^^

.. code-block:: python

   import anvil

   # Load a region file
   region = anvil.Region.from_file('r.0.0.mca')

   # Get a chunk
   chunk = region.get_chunk(0, 0)

   # Get a block
   block = chunk.get_block(0, 0, 0)

   # Display block information
   print(block.id)
   print(block.properties)

World Management
^^^^^^^^^^^^^^^^

.. code-block:: python

   import anvil

   # Load a world
   world = anvil.World('./world_folder')

   # Get block at coordinates
   block = world.get_block(100, 64, 200)

   # Set a block
   world.set_block(anvil.Block('minecraft', 'diamond_block'), 100, 65, 200)

   # Save changes
   world.save()

Using Patterns
^^^^^^^^^^^^^^

.. code-block:: python

   import anvil
   import patterns

   world = anvil.World('./world_folder')

   # Create a cube
   cube = patterns.Cube(
       blocks=[anvil.Block('minecraft', 'diamond_block')],
       point=(200, 160, 200),
       size=(3, 3, 3)
   )
   world.apply(cube.filled())

   # Create a pyramid
   pyramid = patterns.Pyramid(
       blocks=[anvil.Block('minecraft', 'sandstone')],
       point=(300, 160, 200),
       size=(18, 9, 18)
   )
   world.apply(pyramid.filled())

   world.save()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
