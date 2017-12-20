import re
from rbac import  models
from django.utils.safestring import mark_safe

def menu(user_id,current_url):
    """
    根据用户ID，当前URL：获取用户所有菜单以及权限，是否显示，是否展开
    :param user_id: 用户ID
    :param current_url: 当前URL
    :return:
    """
    all_menu_list = models.Menu.objects.all().values('id','caption','parent_id')
    user = models.User.objects.filter(id=user_id).first()
    role_list = models.Role.objects.filter(users__user=user)
    permission_list = models.Permission2Action2Role.objects.filter(role__in=role_list).values('permission__id','permission__url','permission__menu_id','permission__caption').distinct()
    ##### 将权限挂靠到菜单上 ########
    all_menu_dict = {}
    for row in all_menu_list:
        row['child'] = []
        row['status'] = False
        row['opened'] = False
        all_menu_dict[row['id']] = row

    for per in permission_list:
        if not per['permission_menu_id']:
            continue

        item = {
            'id':per['permission__id'],
            'caption':per['permission__caption'],
            'parent_id':per['permission__menu_id'],
            'url':per['permission__url'],
            'status':True,
            'opened':False
        }
        if re.match(per['permission__url'],current_url):
            item['opened'] = True
        pid = item['parent_id']
        all_menu_dict[pid]['child'].append(item)

        #将当前权限前辈status=True
        temp = pid
        while not all_menu_dict[temp]['status']:
            all_menu_dict[temp]['status'] = True
            temp = all_menu_dict[temp]['parent_id']
            if not temp:
                break

        #将当前权限前辈opened = True

        if item['opened']:
            temp1 = pid
            while not all_menu_dict[temp1]['opened']:
                all_menu_dict[temp1]['opened'] = True
                temp1 = all_menu_dict[temp1]['parent_id']
                if not temp1:
                    break
        # ############ 处理菜单和菜单之间的等级关系 ############
        result = []
        for row in all_menu_list:
            if pid:
                all_menu_dict[pid]['child'].append(row)
            else:
                result.append(row)

##################### 结构化处理结果 #####################
        for row in result:
            print(row['caption'],row['status'],row['opened'],row)

        def menu_tree(menu_list):
            tpl1 = """
            <div class='menu-item'>
                <div class='menu-header'>{0}</div>
                <div class='menu-body {2}'>{1}</div>
            </div>
            """
            tpl2 = """
            <a href='{0}' class='{1}'>{2}</a>
            """
            menu_str = ""
            for menu in menu_list:
                if not menu['status']:
                    continue

                if menu.get('url'):
                    menu_str += tpl2.format(menu['url'],'active' if menu['opened'] else "",menu['caption'])
                else:
                    if menu['child']:
                        child_html = menu_tree(menu['child'])
                    else:
                        child_html = ""
                    menu_str += tpl1.format(menu['caption'],child_html,"" if menu['opened'] else 'hide')
            return menu_str
        menu_html = menu_tree(result)
        return menu_html
