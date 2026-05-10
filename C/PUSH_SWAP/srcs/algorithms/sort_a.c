/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_a.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/11 16:02:39 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/13 06:51:07 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	is_sorted(t_stack *a)
{
	t_node	*current;

	if (!a || !a->top)
		return (1);
	current = a->top;
	while (current->next)
	{
		if (current->index > current->next->index)
			return (0);
		current = current->next;
	}
	return (1);
}

void	sort_a(t_stack *a, t_stack *b, int size)
{
	if (is_sorted(a))
		return ;
	if (size == 2)
		sa(a);
	else if (size == 3)
		selectionsort_3(a);
	else if (size <= 5)
		selectionsort_4_5(a, b);
	else
		radix_sort(a, b);
}
