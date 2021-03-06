#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import consistency_group


class TestConsistencyGroup(volume_fakes.TestVolume):

    def setUp(self):
        super(TestConsistencyGroup, self).setUp()

        # Get a shortcut to the TransferManager Mock
        self.consistencygroups_mock = (
            self.app.client_manager.volume.consistencygroups)
        self.consistencygroups_mock.reset_mock()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()


class TestConsistencyGroupCreate(TestConsistencyGroup):

    volume_type = volume_fakes.FakeType.create_one_type()
    new_consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())

    columns = (
        'availability_zone',
        'created_at',
        'description',
        'id',
        'name',
        'status',
        'volume_types',
    )
    data = (
        new_consistency_group.availability_zone,
        new_consistency_group.created_at,
        new_consistency_group.description,
        new_consistency_group.id,
        new_consistency_group.name,
        new_consistency_group.status,
        new_consistency_group.volume_types,
    )

    def setUp(self):
        super(TestConsistencyGroupCreate, self).setUp()
        self.consistencygroups_mock.create.return_value = (
            self.new_consistency_group)
        self.consistencygroups_mock.create_from_src.return_value = (
            self.new_consistency_group)
        self.consistencygroups_mock.get.return_value = (
            self.new_consistency_group)
        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = consistency_group.CreateConsistencyGroup(self.app, None)

    def test_consistency_group_create(self):
        arglist = [
            '--volume-type', self.volume_type.id,
            '--description', self.new_consistency_group.description,
            '--availability-zone',
            self.new_consistency_group.availability_zone,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('description', self.new_consistency_group.description),
            ('availability_zone',
             self.new_consistency_group.availability_zone),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_called_once_with(
            self.volume_type.id)
        self.consistencygroups_mock.get.assert_not_called()
        self.consistencygroups_mock.create.assert_called_once_with(
            self.volume_type.id,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
            availability_zone=self.new_consistency_group.availability_zone,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_consistency_group_create_without_name(self):
        arglist = [
            '--volume-type', self.volume_type.id,
            '--description', self.new_consistency_group.description,
            '--availability-zone',
            self.new_consistency_group.availability_zone,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('description', self.new_consistency_group.description),
            ('availability_zone',
             self.new_consistency_group.availability_zone),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_called_once_with(
            self.volume_type.id)
        self.consistencygroups_mock.get.assert_not_called()
        self.consistencygroups_mock.create.assert_called_once_with(
            self.volume_type.id,
            name=None,
            description=self.new_consistency_group.description,
            availability_zone=self.new_consistency_group.availability_zone,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_consistency_group_create_from_source(self):
        arglist = [
            '--consistency-group-source', self.new_consistency_group.id,
            '--description', self.new_consistency_group.description,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('consistency_group_source', self.new_consistency_group.id),
            ('description', self.new_consistency_group.description),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_not_called()
        self.consistencygroups_mock.get.assert_called_once_with(
            self.new_consistency_group.id)
        self.consistencygroups_mock.create_from_src.assert_called_with(
            None,
            self.new_consistency_group.id,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestConsistencyGroupDelete(TestConsistencyGroup):

    consistency_groups =\
        volume_fakes.FakeConsistencyGroup.create_consistency_groups(count=2)

    def setUp(self):
        super(TestConsistencyGroupDelete, self).setUp()

        self.consistencygroups_mock.get = volume_fakes.FakeConsistencyGroup.\
            get_consistency_groups(self.consistency_groups)
        self.consistencygroups_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = consistency_group.DeleteConsistencyGroup(self.app, None)

    def test_consistency_group_delete(self):
        arglist = [
            self.consistency_groups[0].id
        ]
        verifylist = [
            ("consistency_groups", [self.consistency_groups[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.delete.assert_called_with(
            self.consistency_groups[0].id, False)
        self.assertIsNone(result)

    def test_consistency_group_delete_with_force(self):
        arglist = [
            '--force',
            self.consistency_groups[0].id,
        ]
        verifylist = [
            ('force', True),
            ("consistency_groups", [self.consistency_groups[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.delete.assert_called_with(
            self.consistency_groups[0].id, True)
        self.assertIsNone(result)

    def test_delete_multiple_consistency_groups(self):
        arglist = []
        for b in self.consistency_groups:
            arglist.append(b.id)
        verifylist = [
            ('consistency_groups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for b in self.consistency_groups:
            calls.append(call(b.id, False))
        self.consistencygroups_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_consistency_groups_with_exception(self):
        arglist = [
            self.consistency_groups[0].id,
            'unexist_consistency_group',
        ]
        verifylist = [
            ('consistency_groups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.consistency_groups[0],
                            exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 consistency groups failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.consistencygroups_mock,
                                      self.consistency_groups[0].id)
            find_mock.assert_any_call(self.consistencygroups_mock,
                                      'unexist_consistency_group')

            self.assertEqual(2, find_mock.call_count)
            self.consistencygroups_mock.delete.assert_called_once_with(
                self.consistency_groups[0].id, False
            )


class TestConsistencyGroupList(TestConsistencyGroup):

    consistency_groups = (
        volume_fakes.FakeConsistencyGroup.create_consistency_groups(count=2))

    columns = [
        'ID',
        'Status',
        'Name',
    ]
    columns_long = [
        'ID',
        'Status',
        'Availability Zone',
        'Name',
        'Description',
        'Volume Types',
    ]
    data = []
    for c in consistency_groups:
        data.append((
            c.id,
            c.status,
            c.name,
        ))
    data_long = []
    for c in consistency_groups:
        data_long.append((
            c.id,
            c.status,
            c.availability_zone,
            c.name,
            c.description,
            utils.format_list(c.volume_types)
        ))

    def setUp(self):
        super(TestConsistencyGroupList, self).setUp()

        self.consistencygroups_mock.list.return_value = self.consistency_groups
        # Get the command to test
        self.cmd = consistency_group.ListConsistencyGroup(self.app, None)

    def test_consistency_group_list_without_options(self):
        arglist = []
        verifylist = [
            ("all_projects", False),
            ("long", False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.list.assert_called_once_with(
            detailed=True, search_opts={'all_tenants': False})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_consistency_group_list_with_all_project(self):
        arglist = [
            "--all-projects"
        ]
        verifylist = [
            ("all_projects", True),
            ("long", False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.list.assert_called_once_with(
            detailed=True, search_opts={'all_tenants': True})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_consistency_group_list_with_long(self):
        arglist = [
            "--long",
        ]
        verifylist = [
            ("all_projects", False),
            ("long", True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.list.assert_called_once_with(
            detailed=True, search_opts={'all_tenants': False})
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestConsistencyGroupShow(TestConsistencyGroup):
    columns = (
        'availability_zone',
        'created_at',
        'description',
        'id',
        'name',
        'status',
        'volume_types',
    )

    def setUp(self):
        super(TestConsistencyGroupShow, self).setUp()

        self.consistency_group = (
            volume_fakes.FakeConsistencyGroup.create_one_consistency_group())
        self.data = (
            self.consistency_group.availability_zone,
            self.consistency_group.created_at,
            self.consistency_group.description,
            self.consistency_group.id,
            self.consistency_group.name,
            self.consistency_group.status,
            self.consistency_group.volume_types,
        )
        self.consistencygroups_mock.get.return_value = self.consistency_group
        self.cmd = consistency_group.ShowConsistencyGroup(self.app, None)

    def test_consistency_group_show(self):
        arglist = [
            self.consistency_group.id
        ]
        verifylist = [
            ("consistency_group", self.consistency_group.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.consistencygroups_mock.get.assert_called_once_with(
            self.consistency_group.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
