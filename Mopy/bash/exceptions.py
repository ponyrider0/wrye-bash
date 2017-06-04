# BOLT
# =============================================================================
class BoltError(Exception):
    """Generic error with a string message."""
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return self.message

class AbstractError(BoltError):
    """Coding Error: Abstract code section called."""
    def __init__(self,message=u'Abstract section called.'):
        BoltError.__init__(self,message)

class ArgumentError(BoltError):
    """Coding Error: Argument out of allowed range of values."""
    def __init__(self,message=u'Argument is out of allowed ranged of values.'):
        BoltError.__init__(self,message)

class StateError(BoltError):
    """Error: Object is corrupted."""
    def __init__(self,message=u'Object is in a bad state.'):
        BoltError.__init__(self,message)

class UncodedError(BoltError):
    """Coding Error: Call to section of code that hasn't been written."""
    def __init__(self,message=u'Section is not coded yet.'):
        BoltError.__init__(self,message)

class CancelError(BoltError):
    """User pressed 'Cancel' on the progress meter."""
    def __init__(self,message=u'Action aborted by user.'):
        BoltError.__init__(self, message)

class SkipError(CancelError):
    """User pressed Skipped n operations."""
    def __init__(self):
        CancelError.__init__(self, u'Action skipped by user.')

class PermissionError(BoltError):
    """Wrye Bash doesn't have permission to access the specified file/directory."""
    def __init__(self,message=u'Access is denied.'):
        BoltError.__init__(self,message)

class FileError(BoltError):
    """TES4/Tes4SaveFile Error: File is corrupted."""
    def __init__(self,inName,message):
        BoltError.__init__(self,message)
        self.inName = inName

    def __str__(self):
        if self.inName: # Path or basestring
            return (u'%s: ' % self.inName) + self.message
        return u'Unknown File: ' + self.message

class FileEditError(BoltError):
    """Unable to edit a file"""
    def __init__(self,filePath,message=None):
        message = message or u"Unable to edit file %s." % filePath.s
        BoltError.__init__(self,message)
        self.filePath = filePath

# BAIN
# =============================================================================
class InstallerArchiveError(BoltError): pass

# BSA_FILES
# =============================================================================
class BSAError(Exception): pass

class BSANotImplemented(BSAError): pass

class BSAVersionError(BSAError):
    def __init__(self, version, expected_version):
        super(BSAVersionError, self).__init__(
            u'Unexpected version %r - expected %r' % (
                version, expected_version))

class BSAFlagError(BSAError):
    def __init__(self, msg, flag):
        super(BSAFlagError, self).__init__(msg +  u' (flag %d) unset' % flag)

class BSADecodingError(BSAError):
    def __init__(self, string):
        super(BSADecodingError, self).__init__(
            u'Undecodable string %r' % string)

# BREC
# =============================================================================
# Mod I/O Errors --------------------------------------------------------------
class ModError(FileError):
    """Mod Error: File is corrupted."""
    pass

class ModReadError(ModError):
    """TES4 Error: Attempt to read outside of buffer."""
    def __init__(self,inName,recType,tryPos,maxPos):
        self.recType = recType
        self.tryPos = tryPos
        self.maxPos = maxPos
        if tryPos < 0:
            message = (u'%s: Attempted to read before (%d) beginning of file/buffer.'
                       % (recType,tryPos))
        else:
            message = (u'%s: Attempted to read past (%d) end (%d) of file/buffer.'
                       % (recType,tryPos,maxPos))
        ModError.__init__(self,inName.s,message)

class ModSizeError(ModError):
    """TES4 Error: Record/subrecord has wrong size."""
    def __init__(self, inName, recType, readSize, maxSize, exactSize=True,
                 **kwdargs):
        self.recType = recType
        self.readSize = readSize
        self.maxSize = maxSize
        self.exactSize = exactSize
        if kwdargs.get('oldSkyrim', False):
            messageForm = (u'\nWrye Bash SSE expects a newer format for %s '
                           u'than found.\nLoad and save %s with the Skyrim SE CK\n' % (
                               recType, inName))
        else: messageForm = u''
        if exactSize:
            messageForm += u'%s: Expected size == %d, but got: %d '
        else:
            messageForm += u'%s: Expected size <= %d, but got: %d '
        ModError.__init__(self,inName.s,messageForm % (recType,readSize,maxSize))

class ModUnknownSubrecord(ModError):
    """TES4 Error: Unknown subrecord."""
    def __init__(self,inName,subType,recType):
        ModError.__init__(self,inName,u'Extraneous subrecord (%s) in %s record.'
                          % (subType,recType))

# ENV
# =============================================================================
# Shell (OS) File Operations --------------------------------------------------
class FileOperationError(OSError):
    def __init__(self, errorCode):
        self.errno = errorCode
        Exception.__init__(self, u'FileOperationError: %i' % errorCode)

class AccessDeniedError(FileOperationError):
    def __init__(self):
        self.errno = 5
        Exception.__init__(self, u'FileOperationError: Access Denied')

class InvalidPathsError(FileOperationError):
    def __init__(self, source, target):
        self.errno = 124
        Exception.__init__(self, u'FileOperationError: Invalid paths:'
                                 u'\nsource: %s\ntarget: %s' % (source, target))

class DirectoryFileCollisionError(FileOperationError):
    def __init__(self, source, dest):
        self.errno = -1
        Exception.__init__(self,
                           u'FileOperationError: collision: moving %s to %s' %(source, dest))

class NonExistentDriveError(FileOperationError):
    def __init__(self, failed_paths):
        self.errno = -1
        self.failed_paths = failed_paths
        Exception.__init__(self,u'FileOperationError: non existent drive')

# BOSH
# =============================================================================
class PluginsFullError(BoltError):
    """Usage Error: Attempt to add a mod to plugins when plugins is full."""
    def __init__(self,message=u'Load list is full.'):
        BoltError.__init__(self,message)

# PARSERS
# =============================================================================
class MasterMapError(BoltError):
    """Attempt to map a fid when mapping does not exist."""
    def __init__(self,modIndex):
        BoltError.__init__(self,u'No valid mapping for mod index 0x%02X' % modIndex)

# BARB
# =============================================================================
class BackupCancelled(BoltError):
    # user cancelled operation
    def __init__(self,message=u'Cancelled'):
        BoltError.__init__(self,message)

# _SAVES
# =============================================================================
class SaveFileError(FileError):
    """TES4 Save File Error: File is corrupted."""
    pass

# SAVE_FILES
# =============================================================================
class SaveHeaderError(Exception): pass
