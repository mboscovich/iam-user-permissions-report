import boto3
import json
import pandas

def getPolicyDocument(policyARN):
    iam = boto3.client('iam')
    policy = iam.get_policy(
        PolicyArn =policyARN
    )
    policy_version = iam.get_policy_version(
        PolicyArn=policyARN,
        VersionId=policy['Policy']['DefaultVersionId']
    )
    policyDocument = str(json.dumps(policy_version['PolicyVersion']['Document']['Statement'], indent=4))
    return policyDocument

def getUserManagedPolicies(username):
    user_managed_policies = client.list_attached_user_policies(UserName=username)
    policies = []

    for managed_policy in user_managed_policies['AttachedPolicies']:
        policy = {
            'name':'',
            'type':'',
            'document':''
        }
        policy['name'] = managed_policy['PolicyName']
        policy['type'] = 'Managed (User)'
        policy['document'] = getPolicyDocument(managed_policy['PolicyArn'])
        policies.append(policy)
    return policies

def getUserInlinePolicies(username):
    user_inline_policies = client.list_user_policies(UserName=username)
    policies = []

    for inline_policy in user_inline_policies['PolicyNames']:
        policy = {
            'name':'',
            'type':'',
            'document':''
        }
        policy['name'] = inline_policy
        policy['type'] = 'Inline (User)'
        policy['document'] = str(json.dumps(client.get_user_policy(UserName=username,PolicyName=inline_policy), indent=4))
        policies.append(policy)
    return policies

def getUserGroups(username):
    user_groups = client.list_groups_for_user(UserName=username)
    groups = []
    for group in user_groups['Groups']:
        groups.append((group['GroupName']))
    return groups

def getGroupManagedPolicies(groupname):
    group_managed_policies = client.list_attached_group_policies(GroupName=groupname)
    policies = []

    for managed_policy in group_managed_policies['AttachedPolicies']:
        policy = {
            'name':'',
            'type':'',
            'document':''
        }
        policy['name'] = managed_policy['PolicyName']
        policy['type'] = 'Managed (Group)'
        policy['document'] = getPolicyDocument(managed_policy['PolicyArn'])
        policies.append(policy)
    return policies

def getGroupInlinePolicies(groupname):
    group_inline_policies = client.list_group_policies(GroupName=groupname)
    policies = []

    for inline_policy in group_inline_policies['PolicyNames']:
        policy = {
            'name':'',
            'type':'',
            'document':''
        }
        policy['name'] = inline_policy
        policy['type'] = 'Inline (Group)'
        policy['document'] = str(json.dumps(client.get_group_policy(GroupName=groupname,PolicyName=inline_policy)['PolicyDocument']['Statement'], indent=4))
        policies.append(policy)

    return policies


def printAllUserPolicies(username, policies):
    header = ['User', 'Policy Name', 'Policy type', 'Policy JSON']
    print('| {:1} | {:^4} | {:>4} | {:<3} |'.format(*header))

    for policy in policies:
        table = [
            [username, policy['name'],policy['type'], policy['document']]
        ]

        for row in table:
            print('| {:1} | {:^4} | {:>4} | {:<3} |'.format(*row))

def generateXlsFile(data):
    # Create a Pandas dataframe from some data.
    df = pandas.DataFrame(data)

    # Order the columns if necessary.
    df = df[['User', 'Policy Name', 'Policy type','Policy JSON']]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter('iam-users-permissions-report.xlsx', engine='xlsxwriter')

    # Write the dataframe data to XlsxWriter. Turn off the default header and
    # index and skip one row to allow us to insert a user defined header.
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{'header': column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 12)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
#

client = boto3.client('iam')

users = client.list_users()['Users']
rows = {
    'User': [],
    'Policy Name': [],
    'Policy type': [],
    'Policy JSON': []
}
for user in users:
    print('Processing user: %s' % user['UserName'])
    user_inline_policies = []
    user_managed_policies = []
    group_managed = []
    group_inline = []
    user_managed_policies = getUserManagedPolicies(user['UserName'])
    user_inline_policies = getUserInlinePolicies(user['UserName'])
    groups=getUserGroups(user['UserName'])
    for group in groups:
        group_managed=getGroupManagedPolicies(group)
        group_inline=getGroupInlinePolicies(group)

    all_policies = user_inline_policies + user_managed_policies + group_managed + group_inline
    for policy in all_policies:
        rows['User'].append(user['UserName'])
        rows['Policy Name'].append(policy['name'])
        rows['Policy type'].append(policy['type'])
        rows['Policy JSON'].append(policy['document'])

generateXlsFile(rows)