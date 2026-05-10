/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pb.c                                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/10 07:19:20 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:41:00 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	pb(t_stack *a, t_stack *b)
{
	t_node	*tmp;

	if (a->size <= 0)
		return ;
	tmp = a->top;
	a->top = tmp->next;
	if (a->top)
		a->top->prev = NULL;
	else
		a->bottom = NULL;
	a->size--;
	tmp->prev = NULL;
	tmp->next = b->top;
	if (b->top)
		b->top->prev = tmp;
	else
		b->bottom = tmp;
	b->top = tmp;
	b->size++;
	ft_printf("pb\n");
}
