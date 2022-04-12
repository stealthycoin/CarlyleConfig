from carlyleconfig.plugins import SSMPlugin


class FakeClient:
    def __init__(self):
        self.recorded = []

    def get_parameters(Names):
        print(names)
        self.recorded.append(Names)
        return 'value'


def test_plugin():
    client = FakeClient()
    plugin = SSMPlugin('prefix', client=client)

    assert plugin.factory_name == 'ssm_parameter'

    plugin.add_name('foo')
    plugin.add_name('bar')

    plugin.value_for_name('foo')
    plugin.value_for_name('bar')

    assert client.recorded == ['foo', 'bar']
