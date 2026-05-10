/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   init_stack.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/02 08:06:16 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/03 07:29:07 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

t_stack	*init_stack(t_node *list, int size)
{
	t_stack	*stack;
	t_node	*bottom;

	stack = malloc(sizeof(t_stack));
	if (!stack)
		return (NULL);
	stack->top = list;
	if (!list)
		bottom = NULL;
	else
	{
		bottom = list;
		while (bottom->next)
			bottom = bottom->next;
	}
	stack->bottom = bottom;
	stack->size = size;
	return (stack);
}
