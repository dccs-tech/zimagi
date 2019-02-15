from systems import models
from data.environment import models as env
from data.network import models as network


class NetworkFacade(models.ProviderModelFacade):

    def get_packages(self):
        return super().get_packages() + ['network', 'server']

    def key(self):
        return 'name'
 
    def scope(self, fields = False):
        if fields:
            return ('environment',)
        
        curr_env = env.Environment.facade.get_env()
        if not curr_env:
            return False

        return { 'environment_id': curr_env }


class Network(models.AppProviderModel):

    name = models.CharField(max_length=128)
    type = models.CharField(null=True, max_length=128)
    cidr = models.CharField(null=True, max_length=128)

    environment = models.ForeignKey(env.Environment, related_name='networks', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('environment', 'name')
        facade_class = NetworkFacade

    def __str__(self):
        return "{} ({})".format(self.name, self.cidr)


    def initialize(self, command):
        network_peer, created = network.NetworkPeer.facade.store(self.name, type = self.type)

        self.provider = command.get_provider('network:network', self.type, instance = self)
        self.peer_provider = command.get_provider('network:network_peer', self.type, 
            instance = network_peer
        )
        return True
