/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pa.c                                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/05 20:00:26 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:40:46 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	pa(t_stack *a, t_stack *b)
{
	t_node	*tmp;

	if (b->size <= 0)
		return ;
	tmp = b->top;
	b->top = tmp->next;
	if (b->top)
		b->top->prev = NULL;
	else
		b->bottom = NULL;
	b->size--;
	tmp->prev = NULL;
	tmp->next = a->top;
	if (a->top)
		a->top->prev = tmp;
	else
		a->bottom = tmp;
	a->top = tmp;
	a->size++;
	ft_printf("pa\n");
}
