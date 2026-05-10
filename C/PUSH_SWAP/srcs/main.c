/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/03 19:28:06 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/13 06:50:29 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

//for test
// static void	print_stack(t_stack *stack, char *label)
// {
// 	t_node	*current;

// 	ft_printf("%s (size=%d):\n", label, stack->size);
// 	current = stack->top;
// 	while (current)
// 	{
// 		ft_printf("value=%d index=%d\n", current->value, current->index);
// 		current = current->next;
// 	}
// 	ft_printf("\n");
// }

static void	free_stack_nodes(t_stack *stack)
{
	t_node	*current;
	t_node	*next;

	if (stack && stack->top)
	{
		current = stack->top;
		while (current)
		{
			next = current->next;
			free(current);
			current = next;
		}
	}
}

static void	free_all(int *values, int *indices, t_stack *a, t_stack *b)
{
	if (values)
		free(values);
	if (indices)
		free(indices);
	free_stack_nodes(a);
	free_stack_nodes(b);
	if (a)
		free(a);
	if (b)
		free(b);
}

static int	parse(int argc, char **argv, int *size, int **values)
{
	if (argc < 2)
		return (0);
	if (argc == 2)
		*values = parse_string(argv[1], size);
	else
		*values = parse_clarg(argc, argv, size);
	if (!*values)
		return (0);
	return (1);
}

static int	init_and_sort(int *values, int *indices, int size)
{
	t_node	*list;
	t_stack	*a;
	t_stack	*b;

	list = create_list(values, indices, size);
	if (!list)
		return (0);
	a = init_stack(list, size);
	b = init_stack(NULL, 0);
	if (!a || !b)
		return (free_all(values, indices, a, b), 0);
	sort_a(a, b, size);
	free_all(values, indices, a, b);
	return (1);
}

int	main(int argc, char **argv)
{
	int		size;
	int		*values;
	int		*indices;

	if (!parse(argc, argv, &size, &values))
		return (1);
	indices = normalize(size, values);
	if (!indices)
		return (free (values), ft_printf("Error\n"), 1);
	if (!init_and_sort(values, indices, size))
		return (free(values), free(indices), ft_printf("Error\n"), 1);
	return (0);
}
