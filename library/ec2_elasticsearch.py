#!/usr/bin/python
# encoding: utf-8

# (c) 2015, Jose Armesto <jose@armesto.net>
#
# This file is part of Ansible
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = """
---
module: ec2_elasticsearch
short_description: Creates ElasticSearch cluster on Amazon
description:
  - It depends on boto3

version_added: "2.1"
author: "Jose Armesto (@fiunchinho)"
options:
  name:
    description:
      - The name of the Amazon OpenSearch/ElasticSearch Service domain.
        Domain names are unique across the domains owned by an account within an AWS region.
    required: true
    type: str
  engine_type:
    description:
      - The engine type to use. "ElasticSearch" | "OpenSearch"
    required: false
    type: str
    default: ElasticSearch
  elasticsearch_version:
    description:
      - The version of ElasticSearch or OpenSearch to deploy.
    required: false
    type: str
    default: "2.3"
  region:
    description:
      - The AWS region to use.
    required: true
    aliases: ['aws_region', 'ec2_region']
    type: str
  instance_type:
    description:
      - Type of the instances to use for the cluster. Valid types are: 'm3.medium.elasticsearch'|'m3.large.elasticsearch'|'m3.xlarge.elasticsearch'|'m3.2xlarge.elasticsearch'|'t2.micro.elasticsearch'|'t2.small.elasticsearch'|'t2.medium.elasticsearch'|'r3.large.elasticsearch'|'r3.xlarge.elasticsearch'|'r3.2xlarge.elasticsearch'|'r3.4xlarge.elasticsearch'|'r3.8xlarge.elasticsearch'|'i2.xlarge.elasticsearch'|'i2.2xlarge.elasticsearch'
    required: true
    type: str
  instance_count:
    description:
      - Number of instances for the cluster.
    required: true
    type: int
  dedicated_master:
    description:
      - A boolean value to indicate whether a dedicated master node is enabled.
    required: true
    type: bool
  zone_awareness:
    description:
      - A boolean value to indicate whether zone awareness is enabled.
    required: true
    type: bool
  availability_zone_count:
    description: An integer value to indicate the number of availability zones for a domain when zone awareness is enabled.
      This should be equal to number of subnets if VPC endpoints is enabled.
    required: false
    type: int
  ebs:
    description:
      - Specifies whether EBS-based storage is enabled.
    required: true
    type: bool
  warm_enabled:
    description: True to enable UltraWarm storage.
    required: false
    type: bool
    default: false
  warm_type:
    description: The instance type for the OpenSearch cluster's warm nodes.
    required: false
    type: str
  warm_count:
    description: The number of UltraWarm nodes in the cluster.
    required: false
    type: int
  cold_storage_enabled:
    description: True to enable cold storage.
    required: false
    type: bool
    default: false
  dedicated_master_instance_type:
    description:
      - The instance type for a dedicated master node.
    required: false
    type: str
  dedicated_master_instance_count:
    description:
      - Total number of dedicated master nodes, active and on standby, for the cluster.
    required: false
    type: int
  volume_type:
    description:
      - Specifies the volume type for EBS-based storage. "standard"|"gp2"|"io1"
    required: true
    type: str
  volume_size:
    description:
      - Integer to specify the size of an EBS volume.
    required: true
    type: int
  iops:
    description:
      - The IOPD for a Provisioned IOPS EBS volume (SSD).
    required: false
    type: int
  vpc_subnets:
    description:
      - Specifies the subnet ids for VPC endpoint.
    required: false
    type: list
  vpc_security_groups:
    description:
      - Specifies the security group ids for VPC endpoint.
    required: false
    type: list
  snapshot_hour:
    description:
      - Integer value from 0 to 23 specifying when the service takes a daily automated snapshot of the specified Elasticsearch domain.
    required: false
    type: int
    default: 0
  access_policies:
    description:
      - IAM access policy as a JSON-formatted string.
    required: true
    type: dict
  profile:
    description:
      - What Boto profile use to connect to AWS.
    required: false
    type: str
  encryption_at_rest_enabled:
    description:
      - Should data be encrypted while at rest.
    required: false
    type: bool
  encryption_at_rest_kms_key_id:
    description:
      - If encryption_at_rest_enabled is True, this identifies the encryption key to use 
    required: false
    type: str
  cognito_enabled:
    description:
      - The option to enable Cognito for OpenSearch Dashboards authentication.
    required: false
    type: bool
    default: false
  cognito_user_pool_id:
    description:
      - The Cognito user pool ID for OpenSearch Dashboards authentication.
    required: false
    type: str
  cognito_identity_pool_id:
    description:
      - The Cognito identity pool ID for OpenSearch Dashboards authentication.
    required: false
    type: str
  cognito_role_arn:
    description:
      - The role ARN that provides OpenSearch permissions for accessing Cognito resources.
    required: false
    type: str
requirements:
  - "python >= 2.6"
  - boto3
"""

EXAMPLES = '''

- ec2_elasticsearch:
    name: "my-cluster"
    engine_type: ElasticSearch
    elasticsearch_version: "2.3"
    region: "eu-west-1"
    instance_type: "m3.medium.elasticsearch"
    instance_count: 2
    dedicated_master: True
    zone_awareness: True
    availability_zone_count: 2
    dedicated_master_instance_type: "t2.micro.elasticsearch"
    dedicated_master_instance_count: 2
    ebs: True
    volume_type: "io1"
    volume_size: 10
    iops: 1000
    warm_enabled: true
    warm_type: "ultrawarm1.medium.search"
    warm_count: 1
    cold_storage_enabled: false
    vpc_subnets:
      - "subnet-e537d64a"
      - "subnet-e537d64b"
    vpc_security_groups:
      - "sg-dd2f13cb"
      - "sg-dd2f13cc"
    snapshot_hour: 13
    access_policies: "{{ lookup('file', 'files/cluster_policies.json') | from_json }}"
    profile: "myawsaccount"
'''
try:
    import botocore
    import boto3
    import json

    HAS_BOTO=True
except ImportError:
    HAS_BOTO=False

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            name = dict(required=True),
            instance_type = dict(required=True),
            instance_count = dict(required=True, type='int'),
            dedicated_master = dict(required=True, type='bool'),
            zone_awareness = dict(required=True, type='bool'),
            availability_zone_count = dict(required=False, type='int'),
            dedicated_master_instance_type = dict(),
            dedicated_master_instance_count = dict(type='int'),
            ebs = dict(required=True, type='bool'),
            volume_type = dict(required=True),
            volume_size = dict(required=True, type='int'),
            iops = dict(required=False, type='int'),
            warm_enabled = dict(required=False, type='bool', default=False),
            warm_type = dict(required=False),
            warm_count = dict(required=False, type='int'),
            cold_storage_enabled = dict(required=False, type='bool', default=False),
            access_policies = dict(required=True, type='dict'),
            vpc_subnets = dict(type='list', elements='str', required=False),
            vpc_security_groups = dict(type='list', elements='str', required=False),
            snapshot_hour = dict(required=False, type='int', default=0),
            engine_type = dict(default='ElasticSearch'),
            elasticsearch_version = dict(default='2.3'),
            encryption_at_rest_enabled = dict(type='bool', default=False),
            encryption_at_rest_kms_key_id = dict(required=False),
            cognito_enabled = dict(required=False, type='bool', default=False),
            cognito_user_pool_id = dict(required=False),
            cognito_identity_pool_id = dict(required=False),
            cognito_role_arn = dict(required=False),
    ))

    module = AnsibleModule(
            argument_spec=argument_spec,
            required_if=[
                ('warm_enabled', True, ['warm_type', 'warm_count']),
                ('zone_awareness', True, ['availability_zone_count']),
                ('dedicated_master', True, ['dedicated_master_instance_type', 'dedicated_master_instance_count']),
                ('ebs', True, ['volume_type', 'volume_size']),
                ('cognito_enabled', True, ['cognito_user_pool_id', 'cognito_identity_pool_id', 'cognito_role_arn']),
            ],
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto3 required for this module, install via pip or your package manager')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module, True)
    client = boto3_conn(module=module, conn_type='client', resource='es', region=region, **aws_connect_params)

    cluster_config = {
           'InstanceType': module.params.get('instance_type'),
           'InstanceCount': int(module.params.get('instance_count')),
           'DedicatedMasterEnabled': module.params.get('dedicated_master'),
           'ZoneAwarenessEnabled': module.params.get('zone_awareness'),
           'WarmEnabled': module.params.get('warm_enabled'),
           'ColdStorageOptions': {
              'Enabled': module.params.get('cold_storage_enabled'),
           },
    }
    if module.params.get('zone_awareness'):
        cluster_config['ZoneAwarenessConfig'] = {
            'AvailabilityZoneCount': module.params.get('availability_zone_count'),
        }

    if module.params.get('warm_enabled'):
        cluster_config['WarmType'] = module.params.get('warm_type')
        cluster_config['WarmCount'] = module.params.get('warm_count')

    ebs_options = {
           'EBSEnabled': module.params.get('ebs')
    }

    encryption_at_rest_enabled = module.params.get('encryption_at_rest_enabled') == True
    encryption_at_rest_options = {
        'Enabled': encryption_at_rest_enabled
    }

    if encryption_at_rest_enabled:
        encryption_at_rest_options['KmsKeyId'] = module.params.get('encryption_at_rest_kms_key_id')

    cognito_options = {}
    if module.params.get('cognito_enabled'):
        cognito_options['Enabled'] = True
        cognito_options['UserPoolId'] = module.params.get('cognito_user_pool_id')
        cognito_options['IdentityPoolId'] = module.params.get('cognito_identity_pool_id')
        cognito_options['RoleArn'] = module.params.get('cognito_role_arn')
    else:
      cognito_options['Enabled'] = False

    vpc_options = {}
    vpc_subnets = module.params.get('vpc_subnets')
    if vpc_subnets:
        if isinstance(vpc_subnets, string_types):
            vpc_subnets = [x.strip() for x in vpc_subnets.split(',')]
        vpc_options['SubnetIds'] = vpc_subnets

    vpc_security_groups = module.params.get('vpc_security_groups')
    if vpc_security_groups:
        if isinstance(vpc_security_groups, string_types):
            vpc_security_groups = [x.strip() for x in vpc_security_groups.split(',')]
        vpc_options['SecurityGroupIds'] = vpc_security_groups

    if cluster_config['DedicatedMasterEnabled']:
        cluster_config['DedicatedMasterType'] = module.params.get('dedicated_master_instance_type')
        cluster_config['DedicatedMasterCount'] = module.params.get('dedicated_master_instance_count')

    if ebs_options['EBSEnabled']:
        ebs_options['VolumeType'] = module.params.get('volume_type')
        ebs_options['VolumeSize'] = module.params.get('volume_size')

    if module.params.get('iops') is not None:
        ebs_options['Iops'] = module.params.get('iops')

    snapshot_options = {
        'AutomatedSnapshotStartHour': module.params.get('snapshot_hour')
    }

    changed = False

    try:
        pdoc = json.dumps(module.params.get('access_policies'))
    except Exception as e:
        module.fail_json(msg='Failed to convert the policy into valid JSON: %s' % str(e))

    try:
        response = client.describe_elasticsearch_domain(DomainName=module.params.get('name'))
        status = response['DomainStatus']

        # Modify the provided policy to provide reliable changed detection
        policy_dict = module.params.get('access_policies')
        for statement in policy_dict['Statement']:
            if 'Resource' not in statement:
                # The ES APIs will implicitly set this
                statement['Resource'] = '%s/*' % status['ARN']
                pdoc = json.dumps(policy_dict)

        if status['ElasticsearchClusterConfig'] != cluster_config:
            changed = True

        if status['EBSOptions'] != ebs_options:
            changed = True

        if status['CognitoOptions'] != cognito_options:
            changed = True

        if 'VPCOptions' in status:
            if status['VPCOptions']['SubnetIds'] != vpc_options['SubnetIds']:
                changed = True
            if status['VPCOptions']['SecurityGroupIds'] != vpc_options['SecurityGroupIds']:
                changed = True

        if status['SnapshotOptions'] != snapshot_options:
            changed = True

        current_policy_dict = json.loads(status['AccessPolicies'])
        if current_policy_dict != policy_dict:
            changed = True

        if changed:
            keyword_args = {
                'DomainName': module.params.get('name'),
                'ElasticsearchClusterConfig': cluster_config,
                'EBSOptions': ebs_options,
                'SnapshotOptions': snapshot_options,
                'AccessPolicies': pdoc,
                'CognitoOptions': cognito_options,
            }

            if vpc_options['SubnetIds'] or vpc_options['SecurityGroupIds']:
                keyword_args['VPCOptions'] = vpc_options

            response = client.update_elasticsearch_domain_config(**keyword_args)

    except botocore.exceptions.ClientError as e:
        changed = True

        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            engine_version = "%s_%s" % (module.params.get('engine_type'), module.params.get('elasticsearch_version'))
            keyword_args = {
                'DomainName': module.params.get('name'),
                'EngineVersion': engine_version,
                'EncryptionAtRestOptions': encryption_at_rest_options,
                'ElasticsearchClusterConfig': cluster_config,
                'EBSOptions': ebs_options,
                'SnapshotOptions': snapshot_options,
                'AccessPolicies': pdoc,
                'CognitoOptions': cognito_options,
            }

            if vpc_options['SubnetIds'] or vpc_options['SecurityGroupIds']:
                keyword_args['VPCOptions'] = vpc_options

            response = client.create_elasticsearch_domain(**keyword_args)

        else:
            module.fail_json(msg='Error: %s %s' % (str(e.response['Error']['Code']), str(e.response['Error']['Message'])),)

    # Retrieve response from describe, as create/update differ in their response format
    response = client.describe_elasticsearch_domain(DomainName=module.params.get('name'))
    module.exit_json(changed=changed, response=response)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
