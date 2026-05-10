/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   selectionsort_4_5.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/11 17:12:44 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 07:38:03 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	find_min_pos(t_stack *a)
{
	t_node	*current;
	int		min;
	int		pos;
	int		i;

	if (!a || !a->top)
		return (-1);
	current = a->top;
	min = current->value;
	pos = 0;
	i = 0;
	while (current)
	{
		if (current->value < min)
		{
			min = current->value;
			pos = i;
		}
		current = current->next;
		i++;
	}
	return (pos);
}

static void	move_min_to_top(t_stack *a)
{
	int	pos;

	pos = find_min_pos(a);
	if (pos < 0)
		return ;
	if (pos <= (a->size / 2))
	{
		while (pos > 0)
		{
			ra(a);
			pos--;
		}
	}
	else
	{
		pos = a->size - pos;
		while (pos > 0)
		{
			rra(a);
			pos--;
		}
	}
}

//use for only  size4~5
void	selectionsort_4_5(t_stack *a, t_stack *b)
{
	while (a->size > 3)
	{
		move_min_to_top(a);
		pb(a, b);
	}
	selectionsort_3(a);
	while (b->size)
		pa(a, b);
}
