"""
Cross-cutting helpers shared by the Microsoft IQ deployment scripts.

Modules in this package are deliberately free of Fabric- and Foundry-specific
concepts so they can be imported by either domain package or by the
entry-point scripts (``install_microsoft_iq_solution.py`` /
``remove_microsoft_iq_solution.py``).
"""
