# Спрощена таблиця відповідностей букв
ukrainian_mapping = {
    'А': 1, 'Б': 1,
    'В': 2, 'Г': 2, 'Д': 2, 'Е': 2, 'Є': 2,
    'Ж': 3, 'З': 3, 'И': 3, 'І': 3, 'Ї': 3, 'Й': 3,
    'К': 4, 'Л': 4, 'М': 4,
    'Н': 5, 'О': 5, 'П': 5,
    'Р': 6, 'С': 6, 'Т': 6,
    'У': 7, 'Ф': 7, 'Х': 7, 'Ц': 7,
    'Ч': 8, 'Ш': 8, 'Щ': 8,
    'Ь': 9, 'Ю': 9, 'Я': 9
}

# Хеш функція для імені
def name_to_hash(name, max_len=3):
    name = name.upper()
    code = []
    for char in name[:max_len]:
        code.append(ukrainian_mapping.get(char, 0))
    while len(code) < max_len:
        code.append(0)
    final_number = 0
    for num in code:
        final_number = final_number * 10 + num
    return final_number


# Вузли
class Node:
    def __init__(self, order):
        self.order = order
        self.keys = []
        self.parent = None

class InternalNode(Node):
    def __init__(self, order):
        super().__init__(order)
        self.children = []

class LeafNode(Node):
    def __init__(self, order):
        super().__init__(order)
        self.values = []
        self.next = None


# Основний клас B+ дерева
class BPlusTree:
    def __init__(self, order=4):
        self.root = LeafNode(order)
        self.order = order
        self.first_leaf = self.root  # Зберігаємо найлівіший лист

    def find_leaf(self, key):
        current = self.root
        while isinstance(current, InternalNode):
            i = 0
            while i < len(current.keys) and key >= current.keys[i]:
                i += 1
            current = current.children[i]
        return current

    def insert(self, key, value):
        leaf = self.find_leaf(key)
        i = 0
        while i < len(leaf.keys) and key > leaf.keys[i]:
            i += 1
        leaf.keys.insert(i, key)
        leaf.values.insert(i, value)

        if len(leaf.keys) >= self.order:
            self.split_leaf(leaf)

    def split_leaf(self, leaf):
        mid = len(leaf.keys) // 2
        new_leaf = LeafNode(self.order)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        # Оновлюємо зв'язки між листами
        new_leaf.next = leaf.next
        leaf.next = new_leaf

        # Оновлюємо first_leaf якщо сплітиться перший лист
        if self.first_leaf == leaf:
            self.first_leaf = leaf  

        if leaf == self.root:
            new_root = InternalNode(self.order)
            new_root.keys = [new_leaf.keys[0]]
            new_root.children = [leaf, new_leaf]
            self.root = new_root
            leaf.parent = new_root
            new_leaf.parent = new_root
            return

        self.insert_in_parent(leaf, new_leaf.keys[0], new_leaf)

    def insert_in_parent(self, node, key, new_node):
        parent = node.parent
        if not parent:
            new_root = InternalNode(self.order)
            new_root.keys = [key]
            new_root.children = [node, new_node]
            self.root = new_root
            node.parent = new_root
            new_node.parent = new_root
            return

        i = 0
        while i < len(parent.children) and parent.children[i] != node:
            i += 1

        parent.keys.insert(i, key)
        parent.children.insert(i + 1, new_node)
        new_node.parent = parent

        if len(parent.keys) >= self.order:
            self.split_internal(parent)

    def split_internal(self, internal):
        mid = len(internal.keys) // 2
        new_internal = InternalNode(self.order)
        new_internal.keys = internal.keys[mid + 1:]
        new_internal.children = internal.children[mid + 1:]

        for child in new_internal.children:
            child.parent = new_internal

        up_key = internal.keys[mid]

        internal.keys = internal.keys[:mid]
        internal.children = internal.children[:mid + 1]

        if internal == self.root:
            new_root = InternalNode(self.order)
            new_root.keys = [up_key]
            new_root.children = [internal, new_internal]
            self.root = new_root
            internal.parent = new_root
            new_internal.parent = new_root
            return

        self.insert_in_parent(internal, up_key, new_internal)

    # Простий пошук
    def search(self, key):
        leaf = self.find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None
    
    def range_search(self, key_min, key_max):
        result = []
        node = self.find_leaf(key_min)

        while node:
            for i, key in enumerate(node.keys):
                if key_min <= key <= key_max:
                    result.append(node.values[i])
                elif key > key_max:
                    return result
            node = node.next
        return result


    def delete(self, key):
        leaf = self.find_leaf(key)
        if key in leaf.keys:
            index = leaf.keys.index(key)
            leaf.keys.pop(index)
            leaf.values.pop(index)
            print(f"Ключ {key} успішно видалено.")
        else:
            print(f"Ключ {key} не знайдено.")



    # Друк вузлів дерева (структури)
    def print_tree(self):
        level = [self.root]
        while level:
            next_level = []
            for node in level:
                print(node.keys, end=' | ')
                if isinstance(node, InternalNode):
                    next_level.extend(node.children)
            print()
            level = next_level

    # Друк усіх листів (реальні дані)
    def print_leaves(self):
        node = self.first_leaf
        while node:
            print(node.keys, end=' -> ')
            node = node.next
        print("None")


# --- ТЕСТ ---
tree = BPlusTree(order=4)

# Вставка з виводом
for name in ["Анна", "Богдан", "Василь", "Оля", "Ганна", "Дмитро", "Євгеня", "Жанна"]:
    tree.insert(name_to_hash(name), name)
    print(f"Inserted {name} with hash {name_to_hash(name)}")
    tree.print_leaves()

# Структура дерева
print("\nДерево:")
tree.print_tree()

# Перевірка пошуку
name = "Оля"
key = name_to_hash(name)
result = tree.search(key)
if result:
    print(f"Знайдено: {result}")
else:
    print("Не знайдено")



print("\nДіапазонний пошук [150, 300]:")
results = tree.range_search(150, 300)
for res in results:
    print(res)


print("\nДіапазонний пошук [200, ∞):")
results = tree.range_search(200, float('inf'))
for res in results:
    print(res)


print("\nДіапазонний пошук (-∞, 160]:")
results = tree.range_search(-float('inf'), 160)
for res in results:
    print(res)



# Тест видалення
for name in ["Анна",  "Жанна"]:
    key = name_to_hash(name)
    tree.delete(key)

# Перевіряємо дерево після видалення
tree.print_leaves()
