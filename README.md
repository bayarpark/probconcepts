**Probconcepts** --- Вероятностный анализ формальных понятий на Python

#### Requirements 
+ Python (>= 3.7.7)
+ pandas (>= 1.1.3)
+ dataclasses (>= 0.8)

#### Функционал
- [ ] **Автоматическое извлечение признаков и их вариаций из DataFrame**
- **Поиск в данных:**
- [ ] вероятностных закономерностей (PR),
- [x] сильнейших вероятностных закономерностей (SPL),
- [ ] наиболее спецефических закономерностей (MSR),
- **Классификация на основе PR, SPL, MSR**
- **Возможность интерпретируемости:** 
- [x] извлечение наиболее сильных правил,
- [ ] извлечение наиболее сильных признаков

#### Типы данных
- ***Predicate*** -- поддерживает следующие типы переменных
- [x] Числовые (Real, Int)
- [x] Логические (Bin)
- [x] Номинативные (Nom)

и следующие операции
- [x] `=` -- (все типы); `<`, `<=`, `>`, `>=` -- только для Real и Int
- [x] `interval := x in [a,b]` -- только для Real и Int
- [x] `tails := x not in [a, b]` -- только для Real и Int
- [ ] `func := func(x) -> {T, F}` -- для любых типов данных