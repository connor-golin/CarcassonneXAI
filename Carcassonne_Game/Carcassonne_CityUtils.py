from Carcassonne_Game.GameFeatures import City


def cityConnections(
    self, PlayingTile, Surroundings, ClosingCities, MeepleUpdate, MeepleKey
):
    for i in range(len(PlayingTile.CityOpenings)):
        CityOpenings = PlayingTile.CityOpenings[i]
        AddedMeeples = self.AddMeeple(MeepleUpdate, MeepleKey, "C", i)
        OpeningsQuantity = len(CityOpenings)

        if OpeningsQuantity == 1:
            ClosingCities = cityOneOpening(
                self,
                PlayingTile,
                ClosingCities,
                CityOpenings,
                Surroundings,
                AddedMeeples,
            )
        else:
            ClosingCities = cityMultipleOpenings(
                self,
                PlayingTile,
                ClosingCities,
                CityOpenings,
                OpeningsQuantity,
                Surroundings,
                AddedMeeples,
            )

    return ClosingCities


def cityConnectionIndex(self, Surroundings, CitySide):
    MatchingCityIndex = Surroundings[CitySide].TileCitiesIndex[
        self.MatchingSide[CitySide]
    ]

    while (
        self.BoardCities[MatchingCityIndex].Pointer
        != self.BoardCities[MatchingCityIndex].ID
    ):
        MatchingCityIndex = self.BoardCities[MatchingCityIndex].Pointer

    return MatchingCityIndex


def cityOneOpening(
    self, PlayingTile, ClosingCities, CityOpenings, Surroundings, AddedMeeples
):
    CitySide = CityOpenings[0]

    if Surroundings[CitySide] is None:
        NextCityIndex = len(self.BoardCities)
        self.BoardCities[NextCityIndex] = City(NextCityIndex, 1, 1, AddedMeeples)
        self.BoardCities[NextCityIndex].AddCoordinate(PlayingTile)
        PlayingTile.TileCitiesIndex[CitySide] = NextCityIndex
    else:
        MatchingCityIndex = cityConnectionIndex(self, Surroundings, CitySide)
        MatchingCity = self.BoardCities[MatchingCityIndex]

        MatchingCity.Update(-1, 1, AddedMeeples)
        MatchingCity.AddCoordinate(PlayingTile)

        if MatchingCity.Openings == 0:
            ClosingCities.append(MatchingCityIndex)

        PlayingTile.TileCitiesIndex[CitySide] = MatchingCityIndex

    return ClosingCities


def mergeCities(self, PrimaryCityIndex, MergingCityIndex, connection_reduction=1):
    print("merging")
    PrimaryCity = self.BoardCities[PrimaryCityIndex]
    MergingCity = self.BoardCities[MergingCityIndex]

    # Merge coordinates: add merging city's coordinates to primary city without duplicates
    for tile in MergingCity.tiles:
        PrimaryCity.AddCoordinate(tile)

    # Update the merging city's pointer to point to the primary city
    MergingCity.Pointer = PrimaryCityIndex

    # Reset the merging city's properties (it no longer exists as an independent city)
    MergingCity.Openings = 0
    MergingCity.Value = 0
    MergingCity.Meeples = [0, 0]
    MergingCity.all_coordinates = []

    # remove the secondary city from boardcities
    del self.BoardCities[MergingCityIndex]

    return PrimaryCityIndex


def cityMultipleOpenings(
    self,
    PlayingTile,
    ClosingCities,
    CityOpenings,
    OpeningsQuantity,
    Surroundings,
    AddedMeeples,
):
    ConnectedCities = []

    # Iterate over all sides of the tile that have city openings
    for CitySide in CityOpenings:
        if Surroundings[CitySide] is not None:
            # Check if there is a connection to a pre-existing city
            MatchingCityIndex = cityConnectionIndex(self, Surroundings, CitySide)
            ConnectedCities.append([MatchingCityIndex, CitySide])

    if not ConnectedCities:
        # Create a new city if no connections were found
        NextCityIndex = len(self.BoardCities)
        self.BoardCities[NextCityIndex] = City(
            NextCityIndex, PlayingTile.CityValues, OpeningsQuantity, AddedMeeples
        )
        self.BoardCities[NextCityIndex].AddCoordinate(PlayingTile)
        for CitySide in CityOpenings:
            PlayingTile.TileCitiesIndex[CitySide] = NextCityIndex

    else:
        # Start by assuming the first connected city is the main one
        CombinedCityIndex = ConnectedCities[0][0]

        # Merge all connected cities into the first one
        for MatchingCityIndex, CitySide in ConnectedCities:
            if CombinedCityIndex != MatchingCityIndex:
                # Merge connected cities into the primary city
                CombinedCityIndex = mergeCities(
                    self, CombinedCityIndex, MatchingCityIndex, connection_reduction=1
                )
            else:
                # If the city is already part of the primary city, just update openings
                self.BoardCities[CombinedCityIndex].Update(
                    OpeningsQuantity - len(ConnectedCities),
                    PlayingTile.CityValues,
                    AddedMeeples,
                )
                self.BoardCities[CombinedCityIndex].AddCoordinate(PlayingTile)

        # After merging, update tile city index to point to the merged city
        for CitySide in CityOpenings:
            PlayingTile.TileCitiesIndex[CitySide] = CombinedCityIndex

        # If the merged city is fully closed (no more openings), mark it as closed
        if self.BoardCities[CombinedCityIndex].Openings == 0:
            ClosingCities.append(CombinedCityIndex)

    return ClosingCities


def cityClosures(self, ClosingCities):
    for ClosingCityIndex in ClosingCities:
        ClosingCity = self.BoardCities[ClosingCityIndex]
        ClosingCity.ClosedFlag = True

        if ClosingCity.Meeples[0] > ClosingCity.Meeples[1]:
            self.Scores[0] += 2 * ClosingCity.Value
            self.FeatureScores[0][0] += 2 * ClosingCity.Value
        elif ClosingCity.Meeples[1] > ClosingCity.Meeples[0]:
            self.Scores[1] += 2 * ClosingCity.Value
            self.FeatureScores[1][0] += 2 * ClosingCity.Value
        else:
            self.Scores[0] += 2 * ClosingCity.Value
            self.Scores[1] += 2 * ClosingCity.Value
            self.FeatureScores[0][0] += 2 * ClosingCity.Value
            self.FeatureScores[1][0] += 2 * ClosingCity.Value

        ClosingCity.Value = 0
        self.Meeples[0] += ClosingCity.Meeples[0]
        self.Meeples[1] += ClosingCity.Meeples[1]
