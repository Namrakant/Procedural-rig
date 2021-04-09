"""
########################################################################################################################
# Title        : Name utility module
# Author       : Namrakant Tamrakar
# Created on   : 2/7/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : Functions to work with names and strings
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

def removeSuffix( name ):
    """
    Remove suffix from given name string

    @param name: str, given name string to process
    @return nameNoSuffix: str, name without suffix
    """

    # remove the suffix and return the name without suffix

    edits = name.split( '_' )

    if len( edits ) < 2:
        
        return name

    suffix = '_' + edits[-1]
    nameNoSuffix = name[ : -len(suffix) ]

    return nameNoSuffix