"""Test for the model mapper."""
import json
import unittest
from datetime import date, datetime

from pymultimatic.model import (
    mapper,
    QuickModes,
    OperatingModes,
    ActiveFunction)
from tests.conftest import path


class MapperTest(unittest.TestCase):
    """Test class."""

    def test_map_zone_cooling(self) -> None:
        """Test map zone with cooling."""
        with open(path("files/responses/systemcontrol_ventilation"),
                  'r') as file:
            system = json.loads(file.read())
        zones = mapper.map_zones(system)
        self.assertIsNotNone(zones)

    def test_map_zone_empty(self) -> None:
        """Test map no zone."""
        zone = mapper.map_zone({})
        self.assertIsNone(zone)

    def test_map_zone_no_active_function(self) -> None:
        """Test map a zone without active function"""
        with open(
                path("files/responses/zone_no_active_function"),
                'r') as file:
            zone_file = json.loads(file.read())

        zone = mapper.map_zone(zone_file)
        self.assertEqual(ActiveFunction.STANDBY, zone.active_function)

    def test_map_quick_mode(self) -> None:
        """Test map quick mode."""
        with open(
                path("files/responses/systemcontrol_hotwater_boost"),
                'r') as file:
            system = json.loads(file.read())

        quick_mode = mapper.map_quick_mode(system)
        self.assertEqual(QuickModes.HOTWATER_BOOST.name, quick_mode.name)

    def test_map_quick_mode_quick_veto(self) -> None:
        """Test map quick veto."""
        with open(
                path("files/responses/systemcontrol_quick_veto"),
                'r') as file:
            system = json.loads(file.read())

        quick_mode = mapper.map_quick_mode(system)
        self.assertIsNone(quick_mode)

    def test_map_quick_veto_zone(self) -> None:
        """Test map quick veto zone."""
        with open(
                path("files/responses/systemcontrol_quick_veto"),
                'r') as file:
            system = json.loads(file.read())

        zones = mapper.map_zones(system)

        for zone in zones:
            if zone.id == "Control_ZO2":
                self.assertIsNotNone(zone.quick_veto)
                self.assertEqual(18.5, zone.quick_veto.target)
                self.assertIsNone(zone.quick_veto.duration)
                return
        self.fail("Wrong zone found")

    def test_map_no_quick_mode(self) -> None:
        """Test map no quick mode."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            system = json.loads(file.read())

        quick_mode = mapper.map_quick_mode(system)
        self.assertIsNone(quick_mode)

    def test_map_outdoor_temp(self) -> None:
        """Test map outdoor temperature."""
        with open(
                path('files/responses/systemcontrol'), 'r') as file:
            system = json.loads(file.read())

        temp = mapper.map_outdoor_temp(system)
        self.assertEqual(6.3, temp)

    def test_map_no_outdoor_temp(self) -> None:
        """Test map no outdoor temperature."""
        with open(
                path('files/responses/systemcontrol_no_outside_temp'),
                'r') as file:
            system = json.loads(file.read())

        temp = mapper.map_outdoor_temp(system)
        self.assertIsNone(temp)

    def test_rooms_none(self) -> None:
        """Test map no rooms."""
        rooms = mapper.map_rooms(None)
        self.assertIsNotNone(rooms)
        self.assertEqual(0, len(rooms))

    def test_rooms_empty(self) -> None:
        """Test map empty rooms."""
        rooms = mapper.map_rooms(dict())
        self.assertIsNotNone(rooms)
        self.assertEqual(0, len(rooms))

    def test_rooms_correct(self) -> None:
        """Test map rooms."""
        with open(path('files/responses/rooms'), 'r') as file:
            raw_rooms = json.loads(file.read())

        rooms = mapper.map_rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        room0 = rooms[0]

        self.assertEqual(0, room0.id)
        self.assertEqual("Room 1", room0.name)
        self.assertEqual(OperatingModes.AUTO, room0.operating_mode)
        self.assertEqual(False, room0.window_open)
        self.assertEqual(17.5, room0.target_high)
        self.assertEqual(17.9, room0.temperature)
        self.assertIsNone(room0.quick_veto)
        self.assertEqual(False, room0.child_lock)

    def test_room_empty(self) -> None:
        """Test map empty room."""
        rooms = mapper.map_room({})
        self.assertIsNone(rooms)

    def test_room_quick_veto(self) -> None:
        """Test map quick veto room."""
        with open(path('files/responses/rooms_quick_veto'), 'r') \
                as file:
            raw_rooms = json.loads(file.read())

        rooms = mapper.map_rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        room0 = rooms[0]

        self.assertEqual(0, room0.id)
        self.assertEqual("Room 1", room0.name)
        self.assertEqual(OperatingModes.AUTO, room0.operating_mode)
        self.assertEqual(False, room0.window_open)
        self.assertEqual(20.0, room0.target_high)
        self.assertEqual(17.9, room0.temperature)
        self.assertIsNotNone(room0.quick_veto)
        self.assertEqual(20.0, room0.quick_veto.target)
        self.assertEqual(False, room0.child_lock)

    def test_map_devices(self) -> None:
        """Test map devices."""
        with open(path('files/responses/rooms'), 'r') as file:
            raw_rooms = json.loads(file.read())

        rooms = mapper.map_rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        devices_room0 = rooms[0].devices
        devices_room1 = rooms[1].devices

        self.assertIsNotNone(devices_room0)
        self.assertEqual(1, len(devices_room0))
        self.assertIsNotNone(devices_room1)
        self.assertEqual(2, len(devices_room1))

        self.assertEqual("Device 1", devices_room0[0].name)
        self.assertEqual("R13456789012345678901234", devices_room0[0].sgtin)
        self.assertEqual("VALVE", devices_room0[0].device_type)
        self.assertEqual(True, devices_room0[0].radio_out_of_reach)
        self.assertEqual(True, devices_room0[0].radio_out_of_reach)

        self.assertEqual("Device 1", devices_room1[0].name)
        self.assertEqual("R20123456789012345678900", devices_room1[0].sgtin)
        self.assertEqual("VALVE", devices_room1[0].device_type)
        self.assertEqual(False, devices_room1[0].radio_out_of_reach)
        self.assertEqual(False, devices_room1[0].radio_out_of_reach)

        self.assertEqual("Device 2", devices_room1[1].name)
        self.assertEqual("R20123456789012345678999", devices_room1[1].sgtin)
        self.assertEqual("VALVE", devices_room1[1].device_type)
        self.assertEqual(False, devices_room1[1].radio_out_of_reach)
        self.assertEqual(False, devices_room1[1].radio_out_of_reach)

    def test_holiday_mode_none(self) -> None:
        """Test map no holiday mode."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        holiday_mode = mapper.map_holiday_mode(raw_system)
        self.assertIsNotNone(holiday_mode)
        self.assertFalse(holiday_mode.is_active)
        self.assertIsNotNone(holiday_mode.start_date)
        self.assertIsNotNone(holiday_mode.end_date)
        self.assertIsNotNone(holiday_mode.target)
        self.assertFalse(holiday_mode.is_applied)
        self.assertIsNone(holiday_mode.active_mode)

    def test_holiday_mode(self) -> None:
        """Test map holiday mode."""
        with open(path('files/responses/systemcontrol_holiday'), 'r')\
                as file:
            raw_system = json.loads(file.read())

        holiday_mode = mapper.map_holiday_mode(raw_system)
        quick_mode = mapper.map_quick_mode(raw_system)
        self.assertEqual(QuickModes.HOLIDAY, quick_mode)
        self.assertIsNotNone(holiday_mode)
        self.assertTrue(holiday_mode.is_active)
        self.assertEqual(date(2019, 1, 2), holiday_mode.start_date)
        self.assertEqual(date(2019, 1, 3), holiday_mode.end_date)
        self.assertEqual(15, holiday_mode.target)

    def test_map_circulation(self) -> None:
        """Test map circulation."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        circulation = mapper.map_circulation(raw_system)
        self.assertEqual(OperatingModes.AUTO, circulation.operating_mode)
        self.assertEqual("Control_DHW", circulation.id)
        self.assertIsNone(circulation.temperature)
        self.assertIsNone(circulation.target_high)
        self.assertIsNotNone(circulation.time_program)
        self.assertIsNotNone(circulation.time_program.days['monday']
                             .settings[0].setting)

    def test_hot_water(self) -> None:
        """Test map hot water."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())
        with open(path('files/responses/livereport'), 'r') as file:
            raw_livereport = json.loads(file.read())

        hot_water = mapper.map_hot_water(raw_system, raw_livereport)
        self.assertEqual(44.5, hot_water.temperature)
        self.assertEqual(51, hot_water.target_high)
        self.assertEqual(OperatingModes.AUTO, hot_water.operating_mode)
        self.assertEqual("Control_DHW", hot_water.id)
        self.assertIsNotNone(hot_water.time_program.days['monday']
                             .settings[0].setting)

    def test_no_hotwater(self) -> None:
        """Test map no hot water."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        raw_system['body']['dhw'] = []

        hot_water = mapper.map_hot_water(raw_system, {})
        self.assertIsNone(hot_water)

    def test_hot_water_no_current_temp(self) -> None:
        """Test map hot water no live report."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        hot_water = mapper.map_hot_water(raw_system, json.loads('{}'))
        self.assertEqual(None, hot_water.temperature)
        self.assertEqual(51, hot_water.target_high)
        self.assertEqual(OperatingModes.AUTO, hot_water.operating_mode)
        self.assertEqual("Control_DHW", hot_water.id)

    def test_boiler_status(self) -> None:
        """Test map boiler status."""
        with open(path('files/responses/hvacstate'), 'r') as file:
            hvac = json.loads(file.read())

        boiler_status = mapper.map_boiler_status(hvac)
        self.assertEqual("...", boiler_status.hint)
        self.assertEqual("...", boiler_status.description)
        self.assertEqual("S.8", boiler_status.status_code)
        self.assertEqual("Mode chauffage : Arrêt temporaire après une "
                         "opération de chauffage", boiler_status.title)
        self.assertEqual("VC BE 246/5-3", boiler_status.device_name)
        self.assertFalse(boiler_status.is_error)
        self.assertEqual(datetime.fromtimestamp(1545896904282/1000),
                         boiler_status.timestamp)

    def test_boiler_status_no_live_report(self) -> None:
        """Test map boiler status no live report."""
        with open(path('files/responses/hvacstate'), 'r') as file:
            hvac = json.loads(file.read())

        boiler_status = mapper.map_boiler_status(hvac)
        self.assertEqual("...", boiler_status.hint)
        self.assertEqual("...", boiler_status.description)
        self.assertEqual("S.8", boiler_status.status_code)
        self.assertEqual("Mode chauffage : Arrêt temporaire après une "
                         "opération de chauffage", boiler_status.title)
        self.assertEqual("VC BE 246/5-3", boiler_status.device_name)
        self.assertFalse(boiler_status.is_error)
        self.assertEqual(datetime.fromtimestamp(1545896904282/1000),
                         boiler_status.timestamp)

    def test_boiler_status_empty(self) -> None:
        """Test map empty boiler status."""
        with open(path('files/responses/hvacstate_empty'), 'r')\
                as file:
            hvac = json.loads(file.read())

        boiler_status = mapper.map_boiler_status(hvac)
        self.assertIsNone(boiler_status)

    def test_hot_water_alone(self) -> None:
        """Test map hot water."""
        with open(path('files/responses/hotwater'), 'r') as file:
            raw_hotwater = json.loads(file.read())
        with open(path('files/responses/livereport'), 'r') as file:
            raw_livereport = json.loads(file.read())

        hotwater = mapper.map_hot_water_alone(raw_hotwater, 'control_dhw',
                                              raw_livereport)
        self.assertEqual('control_dhw', hotwater.id)
        self.assertEqual(OperatingModes.AUTO, hotwater.operating_mode)
        self.assertIsNotNone(hotwater.time_program.days['monday']
                             .settings[0].setting)

    def test_hot_water_alone_none(self) -> None:
        """Test map hot water."""
        with open(path('files/responses/livereport'), 'r') as file:
            raw_livereport = json.loads(file.read())

        hotwater = mapper.map_hot_water_alone(None, 'control_dhw',
                                              raw_livereport)
        self.assertIsNone(hotwater)

    def test_circulation_alone(self) -> None:
        """Test map circulation."""
        with open(path('files/responses/circulation'), 'r') as file:
            raw_circulation = json.loads(file.read())

        circulation = mapper.map_circulation_alone(raw_circulation,
                                                   'control_dhw')
        self.assertEqual('control_dhw', circulation.id)
        self.assertEqual(OperatingModes.AUTO, circulation.operating_mode)
        self.assertIsNotNone(circulation.time_program)
        self.assertIsNotNone(circulation.time_program.days['monday']
                             .settings[0].setting)

    def test_circulation_alone_none(self) -> None:
        """Test map circulation."""
        circulation = mapper.map_circulation_alone(None, 'control_dhw')
        self.assertIsNone(circulation)

    def test_no_circulation(self) -> None:
        """Test map no circulation."""
        with open(path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        raw_system['body']['dhw'] = []

        circulation = mapper.map_circulation(raw_system)
        self.assertIsNone(circulation)

    def test_errors_no_error(self) -> None:
        """Test map no errors."""
        with open(path('files/responses/hvacstate'), 'r') as file:
            raw_hvac = json.loads(file.read())

        errors = mapper.map_errors(raw_hvac)
        self.assertEqual(0, len(errors))

    def test_errors_with_errors(self) -> None:
        """Test map hvac errors."""
        with open(path('files/responses/hvacstate_errors'), 'r') \
                as file:
            raw_hvac = json.loads(file.read())

        errors = mapper.map_errors(raw_hvac)
        self.assertEqual(1, len(errors))
        self.assertEqual(mapper._datetime(1562909693021), errors[0].timestamp)
        self.assertEqual('...', errors[0].description)
        self.assertEqual('Défaut : Bus de communication eBus', errors[0].title)
        self.assertEqual('VR920', errors[0].device_name)
        self.assertEqual('F.900', errors[0].status_code)

    def test_map_system_info(self) -> None:
        with open(path(
                'files/responses/facilities'), 'r') as file:
            facilities = json.loads(file.read())
        with open(path(
                'files/responses/gateway'), 'r') as file:
            gateway = json.loads(file.read())
        with open(path(
                'files/responses/hvacstate'), 'r') as file:
            hvac = json.loads(file.read())

        sys_info = mapper.map_system_info(facilities, gateway, hvac, None)
        self.assertEqual('1234567890123456789012345678',
                         sys_info.serial_number)
        self.assertEqual('Home', sys_info.name)
        self.assertEqual('01:23:45:67:89:AB', sys_info.mac_ethernet)
        self.assertEqual('1.2.3', sys_info.firmware)
        self.assertEqual('VR920', sys_info.gateway)
        self.assertEqual('ONLINE', sys_info.online)
        self.assertEqual('UPDATE_NOT_PENDING', sys_info.update)

    def test_map_system_info_specific_serial(self) -> None:
        with open(path(
                'files/responses/facilities_multiple'), 'r') as file:
            facilities = json.loads(file.read())
        with open(path(
                'files/responses/gateway'), 'r') as file:
            gateway = json.loads(file.read())
        with open(path(
                'files/responses/hvacstate'), 'r') as file:
            hvac = json.loads(file.read())

        sys_info = mapper.map_system_info(facilities, gateway, hvac, '888')
        self.assertEqual('888', sys_info.serial_number)
        self.assertEqual('Home2', sys_info.name)
        self.assertEqual('6.6.6', sys_info.firmware)

    def test_map_hvac_sync_state_none(self) -> None:
        self.assertIsNone(mapper.map_hvac_sync_state(None))

    def test_map_reports(self) -> None:
        with open(path('files/responses/livereport'), 'r') as file:
            livereport = json.loads(file.read())
        reports = mapper.map_reports(livereport)
        self.assertEqual(5, len(reports))
        self.assertEqual('VRC700 MultiMatic', reports[0].device_name)
        self.assertEqual('Control_SYS_MultiMatic', reports[0].device_id)
        self.assertEqual('bar', reports[0].unit)
        self.assertEqual(1.9, reports[0].value)
        self.assertEqual('Water pressure', reports[0].name)
        self.assertEqual('WaterPressureSensor', reports[0].id)

    def test_map_reports_no_livereport(self) -> None:
        reports = mapper.map_reports(None)
        self.assertEqual(0, len(reports))

    def test_map_ventilation(self) -> None:
        with open(path('files/responses/systemcontrol_ventilation'), 'r') \
                as file:
            system = json.loads(file.read())

        ventilation = mapper.map_ventilation(system)
        self.assertEqual('_template', ventilation.id)
        self.assertEqual('Ventilation', ventilation.name)
        self.assertEqual(OperatingModes.AUTO, ventilation.operating_mode)
        self.assertEqual(3, ventilation.target_high)
        self.assertEqual(1, ventilation.target_low)
        self.assertIsNone(ventilation.temperature)
