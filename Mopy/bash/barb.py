# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2015 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================

"""Rollback library."""

import cPickle
from os.path import join as _j

import archives
import bash
import bass
import bolt
import bosh
import bush
from . import images_list
from bolt import GPath, deprint
from balt import askSave, askOpen, askWarning, showError, showWarning, \
    showInfo, Link, BusyCursor
from exception import AbstractError, BackupCancelled

#------------------------------------------------------------------------------
class BaseBackupSettings:
    verApp = bass.AppVersion

    def __init__(self, parent=None, path=None, do_quit=False):
        path = GPath(path)
        if path is not None and path.ext == u'' and not path.exists():
            path = None
        if path is None: path = bass.settings['bash.backupPath']
        if path is None: path = bass.dirs['modsBash']
        self.quit = do_quit
        self._dir = path
        self.archive = None
        if path.ext:
            self._dir = path.head
            self.archive = path.tail
        self.parent = parent
        self.verDat = bass.settings['bash.version']
        self.files = {}

    def Apply(self):
        raise AbstractError

    def PromptFile(self):
        raise AbstractError

def SameAppVersion():
    return not cmp(bass.AppVersion, bass.settings['bash.version'])

#------------------------------------------------------------------------------
class BackupSettings(BaseBackupSettings):

    def __init__(self, parent=None, path=None, do_quit=False, backup_images=None):
        BaseBackupSettings.__init__(self, parent, path, do_quit)
        game, dirs = bush.game.fsName, bass.dirs
        for path, name, tmpdir in (
              (dirs['mopy'],                      u'bash.ini',             _j(game, u'Mopy')),
              (dirs['mods'].join(u'Bash'),        u'Table',                _j(game, u'Data', u'Bash')),
              (dirs['mods'].join(u'Docs'),        u'Bash Readme Template', _j(game, u'Data', u'Docs')),
              (dirs['mods'].join(u'Docs'),        u'Bashed Lists',         _j(game, u'Data', u'Docs')),
              (dirs['mods'].join(u'Docs'),        u'wtxt_sand_small.css',  _j(game, u'Data', u'Docs')),
              (dirs['mods'].join(u'Docs'),        u'wtxt_teal.css',        _j(game, u'Data', u'Docs')),
              (dirs['modsBash'],                  u'Table',                _j(game+u' Mods', u'Bash Mod Data')),
              (dirs['modsBash'].join(u'INI Data'),u'Table',                _j(game+u' Mods', u'Bash Mod Data', u'INI Data')),
              (dirs['bainData'],                  u'Converters',           _j(game+u' Mods', u'Bash Installers', u'Bash')),
              (dirs['bainData'],                  u'Installers',           _j(game+u' Mods', u'Bash Installers', u'Bash')),
              (dirs['userApp'],                   u'Profiles',             _j(u'LocalAppData', game)),
              (dirs['userApp'],                   u'bash config',          _j(u'LocalAppData', game)),
              (dirs['saveBase'],                  u'BashProfiles',         _j(u'My Games', game)),
              (dirs['saveBase'],                  u'BashSettings',         _j(u'My Games', game)),
              (dirs['saveBase'],                  u'BashLoadOrders',       _j(u'My Games', game)),
              (dirs['saveBase'],                  u'ModeBase',             _j(u'My Games', game)),
              (dirs['saveBase'],                  u'People',               _j(u'My Games', game)),
                ):
            tmpdir = GPath(tmpdir)
            for ext in (u'',u'.dat',u'.pkl',u'.html',u'.txt'): # hack so the above file list can be shorter, could include rogue files but not very likely
                tpath = tmpdir.join(name+ext)
                fpath = path.join(name+ext)
                if fpath.exists(): self.files[tpath] = fpath
                if fpath.backup.exists(): self.files[tpath.backup] = fpath.backup

        #backup all files in Mopy\Data, Data\Bash Patches\ and Data\INI Tweaks
        for path, tmpdir in (
              (dirs['l10n'],                       _j(game, u'Mopy', u'bash', u'l10n')),
              (dirs['mods'].join(u'Bash Patches'), _j(game, u'Data', u'Bash Patches')),
              (dirs['mods'].join(u'INI Tweaks'),   _j(game, u'Data', u'INI Tweaks')),
                ):
            tmpdir = GPath(tmpdir)
            for name in path.list():
                if path.join(name).isfile():
                    self.files[tmpdir.join(name)] = path.join(name)

        #backup image files if told to
        def _isChanged(ab_path, rel_path):
            for ver_list in images_list.values():
                if  ver_list.get(rel_path.s, -1) == ab_path.size: return False
            return True
        if backup_images: # 1 is changed images only, 2 is all images
            onlyChanged = backup_images == 1
            tmpdir = GPath(_j(game, u'Mopy', u'bash', u'images'))
            path = dirs['images']
            for name in path.list():
                fullname = path.join(name)
                if fullname.isfile() and not name.s.lower() == u'thumbs.db' \
                        and (not onlyChanged or _isChanged(fullname, name)):
                    self.files[tmpdir.join(name)] = fullname

        #backup save profile settings
        savedir = GPath(_j(u'My Games', game))
        profiles = [u''] + bosh.SaveInfos.getLocalSaveDirs()
        for profile in profiles:
            pluginsTxt = (u'Saves', profile, u'plugins.txt')
            loadorderTxt = (u'Saves', profile, u'loadorder.txt')
            for txt in (pluginsTxt, loadorderTxt):
                tpath = savedir.join(*txt)
                fpath = dirs['saveBase'].join(*txt)
                if fpath.exists(): self.files[tpath] = fpath
            table = (u'Saves', profile, u'Bash', u'Table.dat')
            tpath = savedir.join(*table)
            fpath = dirs['saveBase'].join(*table)
            if fpath.exists(): self.files[tpath] = fpath
            if fpath.backup.exists(): self.files[tpath.backup] = fpath.backup

    def Apply(self):
        if not self.PromptFile(): return
        deprint(u'')
        deprint(_(u'BACKUP BASH SETTINGS: ') + self._dir.join(self.archive).s)
        temp_settings_backup_dir = bolt.Path.tempDir()
        try:
            self._backup_settings(temp_settings_backup_dir)
        finally:
            if temp_settings_backup_dir and temp_settings_backup_dir.exists():
                temp_settings_backup_dir.rmtree(safety=u'WryeBash_')

    def _backup_settings(self, temp_dir):
        with BusyCursor():
            # copy all files to ~tmp backup dir
            for tpath,fpath in self.files.iteritems():
                deprint(tpath.s + u' <-- ' + fpath.s)
                fpath.copyTo(temp_dir.join(tpath))
            # dump the version info and file listing
            with temp_dir.join(u'backup.dat').open('wb') as out:
                # data version, if this doesn't match the installed data
                # version, do not allow restore
                cPickle.dump(self.verDat, out, -1)
                # app version, if this doesn't match the installer app version,
                # warn the user on restore
                cPickle.dump(self.verApp, out, -1)
            # create the backup archive in 7z format WITH solid compression
            # may raise StateError
            command = archives.compressCommand(self.archive, self._dir, temp_dir)
            archives.compress7z(command, self._dir, self.archive, temp_dir)
            bass.settings['bash.backupPath'] = self._dir
        self.InfoSuccess()

    def PromptFile(self):
        """Prompt for backup filename - return False if user cancels."""
        if self.archive is None or self._dir.join(self.archive).exists():
            filename = u'Backup Bash Settings %s (%s) v%s-%s.7z' % (
                bush.game.fsName, bolt.timestamp(), self.verDat, self.verApp)
            if not self.quit:
                path = askSave(self.parent, title=_(u'Backup Bash Settings'),
                               defaultDir=self._dir, defaultFile=filename,
                               wildcard=u'*.7z')
                if not path: return False
                self._dir = path.head
                self.archive = path.tail
            elif not self.archive:
                self.archive = filename
        return True

    def WarnFailed(self):
        showWarning(self.parent,
            _(u'There was an error while trying to backup the Bash settings!')+u'\n' +
            _(u'No backup was created.'),
            _(u'Unable to create backup!'))

    def InfoSuccess(self):
        if self.quit: return
        showInfo(self.parent,
            _(u'Your Bash settings have been backed up successfully.')+u'\n' +
            _(u'Backup Path: ')+self._dir.join(self.archive).s+u'\n',
            _(u'Backup File Created'))

#------------------------------------------------------------------------------
class RestoreSettings(BaseBackupSettings):
    def __init__(self, parent=None, path=None, do_quit=False, restore_images=None):
        BaseBackupSettings.__init__(self, parent, path, do_quit)
        if not self.PromptFile():
            raise BackupCancelled()
        self.restore_images = restore_images

    def Apply(self):
        temp_settings_restore_dir = bolt.Path.tempDir()
        try:
            self._Apply(temp_settings_restore_dir)
        finally:
            if temp_settings_restore_dir and temp_settings_restore_dir.exists():
                temp_settings_restore_dir.rmtree(safety=u'WryeBash_')

    def _Apply(self, temp_dir):
        command = archives.extractCommand(self._dir.join(self.archive), temp_dir)
        archives.extract7z(command, self._dir.join(self.archive))
        with temp_dir.join(u'backup.dat').open('rb') as ins:
            self.verDat = cPickle.load(ins)
            self.verApp = cPickle.load(ins)
        if self.ErrorConflict():
            self.WarnFailed()
            return
        elif not self.PromptMismatch():
            raise BackupCancelled()

        deprint(u'')
        deprint(_(u'RESTORE BASH SETTINGS: ') + self._dir.join(self.archive).s)

        # reinitialize bass.dirs using the backup copy of bash.ini if it exists
        game, dirs = bush.game.fsName, bass.dirs
        tmpBash = temp_dir.join(game, u'Mopy', u'bash.ini')
        opts = bash.opts

        bash.SetUserPath(tmpBash.s,opts.userPath)

        bashIni = bass.GetBashIni(tmpBash.s, reload_=True)
        bosh.initBosh(opts.personalPath, opts.localAppDataPath, bashIni)

        # restore all the settings files
        restore_paths = (
                (dirs['mopy'],                      _j(game, u'Mopy')),
                (dirs['mods'].join(u'Bash'),        _j(game, u'Data', u'Bash')),
                (dirs['mods'].join(u'Bash Patches'),_j(game, u'Data', u'Bash Patches')),
                (dirs['mods'].join(u'Docs'),        _j(game, u'Data', u'Docs')),
                (dirs['mods'].join(u'INI Tweaks'),  _j(game, u'Data', u'INI Tweaks')),
                (dirs['modsBash'],                  _j(game+u' Mods', u'Bash Mod Data')),
                (dirs['modsBash'].join(u'INI Data'),_j(game+u' Mods', u'Bash Mod Data', u'INI Data')),
                (dirs['bainData'],                  _j(game+u' Mods', u'Bash Installers', u'Bash')),
                (dirs['userApp'],                   _j(u'LocalAppData', game)),
                (dirs['saveBase'],                  _j(u'My Games', game)),
                )
        if 293 >= self.verApp:
            # restore from old data paths
            restore_paths += (
                (dirs['l10n'],                      _j(game, u'Data')),)
            if self.restore_images:
                restore_paths += (
                    (dirs['images'],                _j(game, u'Mopy', u'images')),)
        else:
            restore_paths += (
                (dirs['l10n'],                      _j(game, u'bash', u'l10n')),)
            if self.restore_images:
                restore_paths += (
                    (dirs['images'],                _j(game, u'Mopy', u'bash', u'images')),)
        for fpath, tpath in restore_paths:
            path = temp_dir.join(tpath)
            if path.exists():
                for name in path.list():
                    if path.join(name).isfile():
                        deprint(GPath(tpath).join(name).s + u' --> '
                                + fpath.join(name).s)
                        path.join(name).copyTo(fpath.join(name))

        #restore savegame profile settings
        tpath = GPath(_j(u'My Games', game, u'Saves'))
        fpath = dirs['saveBase'].join(u'Saves')
        path = temp_dir.join(tpath)
        if path.exists():
            for root_dir, folders, files in path.walk(True,None,True):
                root_dir = GPath(u'.'+root_dir.s)
                for name in files:
                    deprint(tpath.join(root_dir,name).s + u' --> '
                            + fpath.join(root_dir,name).s)
                    path.join(root_dir,name).copyTo(fpath.join(root_dir,name))

        # tell the user the restore is compete and warn about restart
        self.WarnRestart()
        if Link.Frame: # should always exist
            Link.Frame.Destroy()

    def PromptFile(self):
        #prompt for backup filename
        #returns False if user cancels
        if self.archive is None or not self._dir.join(self.archive).exists():
            path = askOpen(self.parent,_(u'Restore Bash Settings'),self._dir,u'',u'*.7z')
            if not path: return False
            self._dir = path.head
            self.archive = path.tail
        return True

    def PromptMismatch(self):
        # return True if same app version or user confirms
        return SameAppVersion() or askWarning(self.parent,
              _(u'The version of Bash used to create the selected backup file does not match the current Bash version!')+u'\n' +
              _(u'Backup v%s does not match v%s') % (self.verApp, bass.settings['bash.version']) + u'\n' +
              u'\n' +
              _(u'Do you want to restore this backup anyway?'),
              _(u'Warning: Version Mismatch!'))

    def ErrorConflict(self):
        # returns positive if the settings are from a newer Bash version
        if cmp(self.verDat, bass.settings['bash.version']) > 0:
            showError(self.parent,
                  _(u'The data format of the selected backup file is newer than the current Bash version!')+u'\n' +
                  _(u'Backup v%s is not compatible with v%s') % (self.verApp, bass.settings['bash.version']) + u'\n' +
                  u'\n' +
                  _(u'You cannot use this backup with this version of Bash.'),
                  _(u'Error: Version Conflict!'))
            return True
        #end if
        return False

    def WarnFailed(self):
        showWarning(self.parent,
            _(u'There was an error while trying to restore your settings from the backup file!')+u'\n' +
            _(u'No settings were restored.'),
            _(u'Unable to restore backup!'))

    def WarnRestart(self):
        if self.quit: return
        showWarning(self.parent,
            _(u'Your Bash settings have been successfully restored.')+u'\n' +
            _(u'Backup Path: ')+self._dir.join(self.archive).s+u'\n' +
            u'\n' +
            _(u'Before the settings can take effect, Wrye Bash must restart.')+u'\n' +
            _(u'Click OK to restart now.'),
            _(u'Bash Settings Restored'))
        Link.Frame.Restart()
