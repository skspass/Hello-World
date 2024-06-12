import argparse
from abc import ABC, abstractmethod

# 定义节点的基类
class Component(ABC):
    def __init__(self, name, level=0, icon=''):
        self.name = name
        self.level = level
        self.icon = icon

    @abstractmethod
    def draw(self, width):
        pass


# 定义容器节点
class Container(Component):
    def __init__(self, name, level=0, icon=''):
        super().__init__(name, level, icon)
        self.children = []

    def add(self, component):
        self.children.append(component)

    def draw(self, width, prefix='', is_last=True):
        pass  # 这个方法会在具体绘制器中实现


# 定义叶节点
class Leaf(Component):
    def draw(self, width, prefix='', is_last=True):
        pass  # 这个方法会在具体绘制器中实现


# 定义抽象工厂类
class AbstractFactory(ABC):
    @abstractmethod
    def create_container_icon(self):
        pass

    @abstractmethod
    def create_leaf_icon(self):
        pass


# 具体工厂类，用于创建特定图标族
class PokerFaceFactory(AbstractFactory):
    def create_container_icon(self):
        return '♢'

    def create_leaf_icon(self):
        return '♤'


class StarFactory(AbstractFactory):
    def create_container_icon(self):
        return '★'

    def create_leaf_icon(self):
        return '☆'


# 定义抽象绘制器类
class Drawer(ABC):
    @abstractmethod
    def draw(self, root):
        pass


# 具体绘制器类，用于树形绘制
class TreeDrawer(Drawer):
    def draw(self, root):
        self._draw_tree(root)

    def _draw_tree(self, component, prefix='', is_last=True):
        connector = '└─' if is_last else '├─'
        print(f"{prefix}{connector} {component.icon} {component.name}")
        prefix += '   ' if is_last else '│  '
        if isinstance(component, Container):
            for i, child in enumerate(component.children):
                is_last = i == len(component.children) - 1
                self._draw_tree(child, prefix, is_last)


# 具体绘制器类，用于矩形绘制
class RectangleDrawer(Drawer):
    def draw(self, root):
        width = self._calculate_width(root)
        self._draw_rectangle(root, width, '', False, True)

    def _calculate_width(self, component, level=0):
        max_width = len(component.icon + component.name) + 2
        if isinstance(component, Container):
            for child in component.children:
                max_width = max(max_width, self._calculate_width(child, level + 1))
        return max_width + 10

    def _draw_rectangle(self, component, width, prefix='', is_last=False, is_first=False):
        line_end = '┐' if is_first else '┤'
        line_beg = '┌' if is_first else '|'

        line_beg = '└' if (is_last and (not isinstance(component, Container) or len(component.children) == 0)) else line_beg
        line_end = '┘' if (is_last and (not isinstance(component, Container) or len(component.children) == 0)) else line_end

        if line_beg == '└':
            prefix = prefix.replace(' ', '─').replace('|', '─').replace('├', '┴')
        if component.name == "root":
            print(f"{line_beg}{prefix}─ {component.name}{component.icon} {'─' * (width - len(component.name) - 3 - len(prefix))}{line_end}")
        else:
            print(f"{line_beg}{prefix}─ {component.name}{component.icon} {'─' * (width - len(component.name) - 4 - len(prefix) - len(component.icon))}{line_end}")
        if not isinstance(component, Container):
            return
        for i, child in enumerate(component.children):
            child_prefix = prefix + '  ├' if (prefix == '' or prefix[-1] != '├') else '  |' + prefix
            if (i == len(component.children) - 1) and component.name == "root":
                is_last = True
            elif i == len(component.children) - 1:
                is_last = is_last
            else:
                is_last = False

            self._draw_rectangle(child, width, child_prefix, is_last=is_last)


# 工厂方法类，用于创建绘制器
class DrawerFactory(ABC):
    @abstractmethod
    def create_drawer(self) -> Drawer:
        pass


class TreeDrawerFactory(DrawerFactory):
    def create_drawer(self) -> Drawer:
        return TreeDrawer()


class RectangleDrawerFactory(DrawerFactory):
    def create_drawer(self) -> Drawer:
        return RectangleDrawer()


# 建造者模式，用于构建JSON结构
class JSONBuilder:
    def __init__(self):
        self.root = Container('root')

    def add_container(self, name, level):
        container = Container(name, level)
        self.root.add(container)
        return container

    def add_leaf(self, container, name, level):
        leaf = Leaf(name, level)
        container.add(leaf)
        return leaf

    def get_result(self):
        return self.root


# 定义迭代器接口
class Iterator(ABC):
    @abstractmethod
    def has_next(self):
        pass

    @abstractmethod
    def next(self):
        pass

# 具体迭代器类，用于遍历数据结构
class JSONIterator(Iterator):
    def __init__(self, structure):
        self.structure = structure
        self.keys = list(structure.keys())
        self.index = 0

    def has_next(self):
        return self.index < len(self.keys)

    def next(self):
        if self.has_next():
            key = self.keys[self.index]
            value = self.structure[key]
            self.index += 1
            return key, value
        else:
            raise StopIteration

# 主类，负责加载和展示JSON数据
class FunnyJsonExplorer:
    def __init__(self, drawer_factory, icon_factory):
        self.drawer_factory = drawer_factory
        self.icon_factory = icon_factory

    def load(self, iterator):
        builder = JSONBuilder()
        while iterator.has_next():
            key, value = iterator.next()
            container = builder.add_container(key, 1)
            container.icon = self.icon_factory.create_container_icon()
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    leaf = builder.add_leaf(container, sub_key, 2)
                    leaf.icon = self.icon_factory.create_leaf_icon()
        return builder.get_result()

    def show(self, structure):
        iterator = JSONIterator(structure)
        root = self.load(iterator)
        drawer = self.drawer_factory.create_drawer()
        drawer.draw(root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON Explorer with different drawing styles and icon sets.")
    parser.add_argument('-d', '--drawer', choices=['tree', 'rectangle'], required=True, help='Choose the drawer type (tree or rectangle).')
    parser.add_argument('-i', '--icon', choices=['poker', 'star'], required=True, help='Choose the icon set (poker or star).')
    args = parser.parse_args()

    structure = {
        'oranges': {
            'mandarin': {
                'clementine': None,
                'tangerine: cheap & juicy!': None
            }
        },
        'apples': {
            'gala': None
        }
    }

    if args.drawer == 'tree':
        drawer_factory = TreeDrawerFactory()
    elif args.drawer == 'rectangle':
        drawer_factory = RectangleDrawerFactory()

    if args.icon == 'poker':
        icon_factory = PokerFaceFactory()
    elif args.icon == 'star':
        icon_factory = StarFactory()

    explorer = FunnyJsonExplorer(drawer_factory, icon_factory)
    explorer.show(structure)

