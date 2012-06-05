#
# Generated Makefile - do not edit!
#
# Edit the Makefile in the project folder instead (../Makefile). Each target
# has a -pre and a -post target defined where you can add customized code.
#
# This makefile implements configuration specific macros and targets.


# Environment
MKDIR=mkdir
CP=cp
GREP=grep
NM=nm
CCADMIN=CCadmin
RANLIB=ranlib
CC=gcc.exe
CCC=g++.exe
CXX=g++.exe
FC=gfortran
AS=as.exe

# Macros
CND_PLATFORM=MinGW-Windows
CND_DLIB_EXT=dll
CND_CONF=Release
CND_DISTDIR=dist
CND_BUILDDIR=build

# Include project Makefile
include Makefile

# Object Directory
OBJECTDIR=${CND_BUILDDIR}/${CND_CONF}/${CND_PLATFORM}

# Object Files
OBJECTFILES= \
	${OBJECTDIR}/main.o \
	${OBJECTDIR}/Common/IO.o \
	${OBJECTDIR}/Common/CTemplateWrap.o \
	${OBJECTDIR}/Common/V8Engine.o


# C Compiler Flags
CFLAGS=

# CC Compiler Flags
CCFLAGS=
CXXFLAGS=

# Fortran Compiler Flags
FFLAGS=

# Assembler Flags
ASFLAGS=

# Link Libraries and Options
LDLIBSOPTIONS=-L../../dev.tools/MinGW/msys/1.0/local/lib -L../../dev.tools/MinGW/msys/1.0/home/tinyms/v8 -lctemplate -lv8

# Build Targets
.build-conf: ${BUILD_SUBPROJECTS}
	"${MAKE}"  -f nbproject/Makefile-${CND_CONF}.mk ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/matty.exe

${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/matty.exe: ${OBJECTFILES}
	${MKDIR} -p ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}
	${LINK.cc} -o ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/matty ${OBJECTFILES} ${LDLIBSOPTIONS} 

${OBJECTDIR}/main.o: main.cpp 
	${MKDIR} -p ${OBJECTDIR}
	${RM} $@.d
	$(COMPILE.cc) -O2 -I../../dev.tools/MinGW/msys/1.0/local/include -I../../dev.tools/MinGW/msys/1.0/home/tinyms/v8/include -MMD -MP -MF $@.d -o ${OBJECTDIR}/main.o main.cpp

${OBJECTDIR}/Common/IO.o: Common/IO.cpp 
	${MKDIR} -p ${OBJECTDIR}/Common
	${RM} $@.d
	$(COMPILE.cc) -O2 -I../../dev.tools/MinGW/msys/1.0/local/include -I../../dev.tools/MinGW/msys/1.0/home/tinyms/v8/include -MMD -MP -MF $@.d -o ${OBJECTDIR}/Common/IO.o Common/IO.cpp

${OBJECTDIR}/Common/CTemplateWrap.o: Common/CTemplateWrap.cpp 
	${MKDIR} -p ${OBJECTDIR}/Common
	${RM} $@.d
	$(COMPILE.cc) -O2 -I../../dev.tools/MinGW/msys/1.0/local/include -I../../dev.tools/MinGW/msys/1.0/home/tinyms/v8/include -MMD -MP -MF $@.d -o ${OBJECTDIR}/Common/CTemplateWrap.o Common/CTemplateWrap.cpp

${OBJECTDIR}/Common/V8Engine.o: Common/V8Engine.cpp 
	${MKDIR} -p ${OBJECTDIR}/Common
	${RM} $@.d
	$(COMPILE.cc) -O2 -I../../dev.tools/MinGW/msys/1.0/local/include -I../../dev.tools/MinGW/msys/1.0/home/tinyms/v8/include -MMD -MP -MF $@.d -o ${OBJECTDIR}/Common/V8Engine.o Common/V8Engine.cpp

# Subprojects
.build-subprojects:

# Clean Targets
.clean-conf: ${CLEAN_SUBPROJECTS}
	${RM} -r ${CND_BUILDDIR}/${CND_CONF}
	${RM} ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/matty.exe

# Subprojects
.clean-subprojects:

# Enable dependency checking
.dep.inc: .depcheck-impl

include .dep.inc
