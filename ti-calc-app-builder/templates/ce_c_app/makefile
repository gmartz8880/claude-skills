# ----------------------------------------------------------------------------
# TI-84 Plus CE C app - CE C/C++ Toolchain (CEdev v13+) makefile
# Build:  make            -> bin/<NAME>.8xp
# Clean:  make clean
# ----------------------------------------------------------------------------
NAME        = MYAPP
ICON        = icon.png
DESCRIPTION = "My CE App"
COMPRESSED  = YES
ARCHIVED    = YES

# -Oz = smallest code (fast load, less flash/RAM); -Wall -Wextra catch bugs early
CFLAGS   = -Wall -Wextra -Oz
CXXFLAGS = -Wall -Wextra -Oz

include $(shell cedev-config --makefile)
