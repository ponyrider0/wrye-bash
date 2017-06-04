class BoltError(Exception):
    """Generic error with a string message."""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class AbstractError(BoltError):
    """Coding Error: Abstract code section called."""
    def __init__(self, message=u'Abstract section called.'):
        super(AbstractError, self).__init__(message)

class ArgumentError(BoltError):
    """Coding Error: Argument out of allowed range of values."""
    def __init__(self, message=u'Argument is out of allowed ranged of values.'):
        super(ArgumentError, self).__init__(message)

class StateError(BoltError):
    """Error: Object is corrupted."""
    def __init__(self, message=u'Object is in a bad state.'):
        super(StateError, self).__init__(message)

class UncodedError(BoltError):
    """Coding Error: Call to section of code that hasn't been written."""
    def __init__(self, message=u'Section is not coded yet.'):
        super(UncodedError, self).__init__(message)

class CancelError(BoltError):
    """User pressed 'Cancel' on the progress meter."""
    def __init__(self, message=u'Action aborted by user.'):
        super(CancelError, self).__init__(message)

class SkipError(CancelError):
    """User pressed Skipped n operations."""
    def __init__(self):
        super(SkipError, self).__init__(u'Action skipped by user.')

class PermissionError(BoltError):
    """Wrye Bash doesn't have permission to access the specified file/directory."""
    def __init__(self, message=u'Access is denied.'):
        super(PermissionError, self).__init__(message)

class FileError(BoltError):
    """TES4/Tes4SaveFile Error: File is corrupted."""
    def __init__(self, in_name, message):
        ## type: (Union[Path, unicode], unicode) -> None
        super(FileError, self).__init__(message)
        self.in_name = in_name

    def __str__(self):
        return u'%s: %s' % ((self.in_name or u'Unknown File'), self.message)

class SaveFileError(FileError):
    """TES4 Save File Error: File is corrupted."""
    pass

class FileEditError(BoltError):
    """Unable to edit a file"""
    def __init__(self, file_path, message=None):
        message = message or (u'Unable to edit file %s.' % file_path.s)
        super(FileEditError, self).__init__(message)
        self.filePath = file_path

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
        super(BSAFlagError, self).__init__(u'%s (flag %d) unset' % (msg, flag))

class BSADecodingError(BSAError):
    def __init__(self, text):
        super(BSADecodingError, self).__init__(u'Undecodable string %r' % text)

# BREC
# =============================================================================
# Mod I/O Errors --------------------------------------------------------------
class ModError(FileError):
    """Mod Error: File is corrupted."""
    pass

class ModReadError(ModError):
    """TES4 Error: Attempt to read outside of buffer."""
    def __init__(self, in_name, rec_type, try_pos, max_pos):
        self.rec_type = rec_type
        self.try_pos = try_pos
        self.max_pos = max_pos
        if try_pos < 0:
            message = (u'%s: Attempted to read before (%d) beginning of file/buffer.'
                       % (rec_type, try_pos))
        else:
            message = (u'%s: Attempted to read past (%d) end (%d) of file/buffer.'
                       % (rec_type, try_pos, max_pos))
        super(ModReadError, self).__init__(in_name.s, message)

class ModSizeError(ModError):
    """TES4 Error: Record/subrecord has wrong size."""
    def __init__(self, in_name, rec_type, read_size, max_size, exact_size=True,
                 old_skyrim=False):
        self.rec_type = rec_type
        self.read_size = read_size
        self.max_size = max_size
        self.exact_size = exact_size
        if old_skyrim:
            message_form = (u'\nWrye Bash SSE expects a newer format for %s '
                            u'than found.\nLoad and save %s with the Skyrim '
                            u'SE CK\n' % (rec_type, in_name))
        else: message_form = u''
        op = '==' if exact_size else '<='
        message_form += u'%s: Expected size %s %d, but got: %d '
        super(ModSizeError, self).__init__(
            in_name.s, message_form % (rec_type, op, read_size, max_size))

# ENV
# =============================================================================
# Shell (OS) File Operations --------------------------------------------------
class FileOperationError(OSError):
    def __init__(self, error_code, message=None):
        self.errno = error_code
        Exception.__init__(self, u'FileOperationError: %s'
                                 % (message or unicode(error_code)))

class AccessDeniedError(FileOperationError):
    def __init__(self):
        super(AccessDeniedError, self).__init__(5, u'Access Denied')

class InvalidPathsError(FileOperationError):
    def __init__(self, source, target):
        # type: (unicode, unicode) -> None
        super(InvalidPathsError, self).__init__(
            124, u'Invalid paths:\nsource: %s\ntarget: %s' % (source, target))

class DirectoryFileCollisionError(FileOperationError):
    def __init__(self, source, dest):
        ## type: (Path, Path) -> None     # from bolt so lets not import this
        super(DirectoryFileCollisionError, self).__init__(
            -1, u'collision: moving %s to %s' % (source, dest))

class NonExistentDriveError(FileOperationError):
    def __init__(self, failed_paths):
        self.failed_paths = failed_paths
        super(NonExistentDriveError, self).__init__(-1, u'non existent drive')

# BOSH
# =============================================================================
class PluginsFullError(BoltError):
    """Usage Error: Attempt to add a mod to plugins when plugins is full."""
    def __init__(self, message=u'Load list is full.'):
        super(PluginsFullError, self).__init__(message)

# PARSERS
# =============================================================================
class MasterMapError(BoltError):
    """Attempt to map a fid when mapping does not exist."""
    def __init__(self, modIndex):
        super(MasterMapError, self).__init__(
            u'No valid mapping for mod index 0x%02X' % modIndex)

# BARB
# =============================================================================
class BackupCancelled(BoltError):
    # user cancelled operation
    def __init__(self, message=u'Cancelled'):
        super(BackupCancelled, self).__init__(message)

# SAVE_FILES
# =============================================================================
class SaveHeaderError(Exception): pass
