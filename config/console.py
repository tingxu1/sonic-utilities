import click
import utilities_common.cli as clicommon

#
# 'console' group ('config console ...')
#
@click.group('console')
def console():
    """Console-related configuration tasks"""
    pass

#
# 'console enable' group ('config console enable')
#
@console.command('enable')
@clicommon.pass_db
def enable_console_switch(db):
    """Enable console switch"""
    config_db = db.cfgdb

    table = "CONSOLE_SWITCH"
    dataKey1 = 'console_mgmt'
    dataKey2 = 'enabled'

    data = { dataKey2 : "yes" }
    config_db.mod_entry(table, dataKey1, data)

#
# 'console disable' group ('config console disable')
#
@console.command('disable')
@clicommon.pass_db
def disable_console_switch(db):
    """Disable console switch"""
    config_db = db.cfgdb

    table = "CONSOLE_SWITCH"
    dataKey1 = 'console_mgmt'
    dataKey2 = 'enabled'

    data = { dataKey2 : "no" }
    config_db.mod_entry(table, dataKey1, data)

#
# 'console add' group ('config console add ...')
#
@console.command('add')
@clicommon.pass_db
@click.argument('linenum', metavar='<line_number>', required=True, type=click.IntRange(0, 65535))
@click.option('--baud', '-b', metavar='<baud>', required=True, type=click.INT)
@click.option('--flowcontrol', '-f', metavar='<flow_control>', required=False, is_flag=True)
@click.option('--devicename', '-d', metavar='<device_name>', required=False)
def add_console_setting(db, linenum, baud, flowcontrol, devicename):
    """Add Console-realted configuration tasks"""
    config_db = db.cfgdb

    table = "CONSOLE_PORT"
    dataKey1 = 'baud_rate'
    dataKey2 = 'flow_control'
    dataKey3 = 'remote_device'

    ctx = click.get_current_context()
    data = config_db.get_entry(table, linenum)
    if data:
        ctx.fail("Trying to add console port setting, which is already exists.")
    else:
        console_entry = { dataKey1: baud }
        console_entry[dataKey2] = "1" if flowcontrol else "0"

        if devicename:
            if isExistingSameDevice(config_db, devicename, table):
                ctx.fail("Given device name {} has been used. Please enter a valid device name or remove the existing one !!".format(devicename))
            console_entry[dataKey3] = devicename

        config_db.set_entry(table, linenum, console_entry)


#
# 'console del' group ('config console del ...')
#
@console.command('del')
@clicommon.pass_db
@click.argument('linenum', metavar='<line_number>', required=True, type=click.IntRange(0, 65535))
def remove_console_setting(db, linenum):
    """Remove Console-related configuration tasks"""
    config_db = db.cfgdb

    table = "CONSOLE_PORT"

    data = config_db.get_entry(table, linenum)
    if data:
        config_db.mod_entry(table, linenum, None)
    else:
        ctx = click.get_current_context()
        ctx.fail("Trying to delete console port setting, which is not present.")

#
# 'console remote_device' group ('config console remote_device ...')
#
@console.command('remote_device')
@clicommon.pass_db
@click.argument('linenum', metavar='<line_number>', required=True, type=click.IntRange(0, 65535))
@click.argument('devicename', metavar='<device_name>', required=False)
def upate_console_remote_device_name(db, linenum, devicename):
    """Update remote device name for a console line"""
    config_db = db.cfgdb
    ctx = click.get_current_context()

    table = "CONSOLE_PORT"
    dataKey = 'remote_device'

    data = config_db.get_entry(table, linenum)
    if data:
        if dataKey in data and devicename == data[dataKey]:
            # do nothing if the device name is same with existing configurtion
            return
        elif not devicename:
            # remove configuration key from console setting if user not give a remote device name
            data.pop(dataKey, None)
            config_db.mod_entry(table, linenum, data)
        elif isExistingSameDevice(config_db, devicename, table):
            ctx.fail("Given device name {} has been used. Please enter a valid device name or remove the existing one !!".format(devicename))
        else:
            data[dataKey] = devicename
            config_db.mod_entry(table, linenum, data)
    else:
        ctx.fail("Trying to update console port setting, which is not present.")

#
# 'console baud' group ('config console baud ...')
#
@console.command('baud')
@clicommon.pass_db
@click.argument('linenum', metavar='<line_number>', required=True, type=click.IntRange(0, 65535))
@click.argument('baud', metavar='<baud>', required=True, type=click.INT)
def update_console_baud(db, linenum, baud):
    """Update baud for a console line"""
    config_db = db.cfgdb
    ctx = click.get_current_context()

    table = "CONSOLE_PORT"
    dataKey = 'baud_rate'

    data = config_db.get_entry(table, linenum)
    if data:
        baud = str(baud)
        if dataKey in data and baud == data[dataKey]:
            # do nothing if the baud is same with existing configurtion
            return
        else:
            data[dataKey] = baud
            config_db.mod_entry(table, linenum, data)
    else:
        ctx.fail("Trying to update console port setting, which is not present.")

#
# 'console flow_control' group ('config console flow_control ...')
#
@console.command('flow_control')
@clicommon.pass_db
@click.argument('mode', metavar='<mode>', required=True, type=click.Choice(["enable", "disable"]))
@click.argument('linenum', metavar='<line_number>', required=True, type=click.IntRange(0, 65535))
def update_console_flow_control(db, mode, linenum):
    """Update flow control setting for a console line"""
    config_db = db.cfgdb
    ctx = click.get_current_context()

    table = "CONSOLE_PORT"
    dataKey = 'flow_control'

    innerMode = "1" if mode == "enable" else "0"

    data = config_db.get_entry(table, linenum)
    if data:
        if dataKey in data and innerMode == data[dataKey]:
            # do nothing if the flow control setting is same with existing configurtion
            return
        else:
            data[dataKey] = innerMode
            config_db.mod_entry(table, linenum, data)
    else:
        ctx.fail("Trying to update console port setting, which is not present.")

def isExistingSameDevice(config_db, deviceName, table):
    """Check if the given device name is conflict with existing device"""
    settings = config_db.get_table(table)
    for key,values in settings.items():
        if "remote_device" in values and deviceName == values["remote_device"]:
            return True

    return False
