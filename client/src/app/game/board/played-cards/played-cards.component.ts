import { Component, OnInit } from '@angular/core';
import { GameService } from '../../game.service';
import { PlayedCard, PlayOrder } from '../../types/played.card.type';

@Component({
	selector: 'app-played-cards',
	templateUrl: './played-cards.component.html',
	styleUrls: ['./played-cards.component.css']
})
export class PlayedCardsComponent implements OnInit {

	otherPlayedCards: PlayedCard[];
	ownPlayedCard: PlayedCard;

	constructor(private game: GameService) { }

	ngOnInit(): void {
		this.game.getObservableBoard().subscribe(board => {
			this.ownPlayedCard = board.played_cards[0];
			this.otherPlayedCards = board.played_cards.slice(1);
		});
	}

	getOrderClass(playedCard: PlayedCard) {
		return PlayOrder[playedCard.order];
	}

	next() {
		this.game.next();
	}

}
